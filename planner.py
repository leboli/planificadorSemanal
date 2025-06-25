from pyomo.environ import *

class planner():
    def __init__(self, fixed_activities, variable_activities, number_of_ts):
        self.fixed_activities = fixed_activities  # list of fixedActivity
        self.variable_activities = variable_activities  # list of variableActivity
        self.number_of_ts = number_of_ts  # total number of time slots in the schedule (e.g., 168 = 1 week in hours)

    def buildModel2(self):
        print("Building model...")

        model = ConcreteModel()

        # Set total activities and time slots
        num_fixed_activities = len(self.fixed_activities)
        num_variable_activities = len(self.variable_activities)
        num_total_activities = num_fixed_activities + num_variable_activities

        model.activities = Set(initialize=range(num_total_activities))
        model.time_slots = Set(initialize=range(self.number_of_ts))
        model.days = Set(initialize=range(1,8))

        def day_of(ts):
            return 1 + ts//(self.number_of_ts//7)

        # -------------------------- VARIABLE DEFINITION --------------------------
        # Binary variable x[a, t]: 1 if activity a is assigned to time slot t
        model.x = Var(model.activities, model.time_slots, domain=Binary)

        # Start of block variable
        model.start_block = Var(self.model.activities, self.model.time_slots, domain=Binary)

        # Transition variables
        model.transition = Var(self.model.activities, self.model.activities, self.model.time_slots, domain=Binary) 

        # Segment variables (h_{a,d,k}) y (y_{a,d,k})
        model.h = {}
        model.y = {}
        max_k = max(len(var.utility.segments) for var in self.variable_activities)

        model.had = Var(model.activities, model.days, domain = NonNegativeIntegers)
        model.ha = Var(model.activities, domain = NonNegativeIntegers)

        model.H = {}
        model.u = {}

        model.W = {}
        model.Lmin = {}
        model.Lmax = {}
        model.Sa = {}
        model.Kad = {}
        model.ppt = {}

        for t in range(self.number_of_ts):
            model.ppt[t] = day_of(t)


        for idx, var_act in enumerate(self.variable_activities):
            a_idx = num_fixed_activities + idx
            model.W[a_idx] = var_act.allowed_ts
            model.Lmin[a_idx] = var_act.min_adjacent_ts
            model.Lmax[a_idx] = var_act.max_adjacent_ts
            model.Sa[a_idx] = [t for t in range(self.number_of_ts) if t + var_act.min_adjacent_ts - 1 <=self.number_of_ts]

            for d in range(1, 8):
                segments = var_act.utility[d-1].segments
                utilities = var_act.utility[d-1].utilities_per_segment
                K = len(utilities)
                for k in range(1, K + 1):
                    model.h[a_idx, d, k] = Var(domain=NonNegativeIntegers)
                    model.y[a_idx, d, k] = Var(domain=Binary)
                    model.H[a_idx, d, k] = segments[k-1] if k > 0 else 0
                    model.u[a_idx, d, k] = utilities[k-1]
                model.H[a_idx, d, 0] = 0

        # Set time_slots to 1 for fixed activities
        for index, fixed_act in enumerate(self.fixed_activities):
            for ts in fixed_act.assigned_ts:
                model.x[index, ts].fix(1)

        # The first x are fixed activities, the following are variable. model.x[0,t] to model.x[num_fixed_activities-1, t] are all fixed activities
        offset = num_fixed_activities

        # Prevent variable activities from being scheduled in disallowed slots
        for index, var_act in enumerate(self.variable_activities):
            for ts in range(self.number_of_ts):
                if ts not in var_act.allowed_ts:
                    model.x[index + offset, ts].fix(0)


        # -------------------------- CONSTRAINTS --------------------------

        # At most one activity per time slot
        model.one_activity_per_slot = ConstraintList()
        for ts in model.time_slots:
            model.one_activity_per_slot.add( sum(model.x[act, ts] for act in model.activities) <= 1 )

        # Max/min time slots per variable activity
        model.min_constraints = ConstraintList()
        model.max_constraints = ConstraintList()
        for index, variable_act in enumerate(self.variable_activities):
            a_idx = offset + index
            model.min_constraints.add( sum(self.model.x[a_idx, t] for t in range(self.number_of_ts)) >= variable_act.min_ts )
            model.max_constraints.add( sum(self.model.x[a_idx, t] for t in range(self.number_of_ts)) <= variable_act.max_ts )

        # Fragmentation constraints (min/max block size per activity)
        model.fragmentation_restrictions = ConstraintList()
        for index, variable in enumerate(self.variable_activities):
            a_idx = offset + index
            min_len = variable.min_adjacent_ts
            max_len = variable.max_adjacent_ts

            for t in range(self.number_of_ts):
                if t + min_len - 1 < self.number_of_ts:
                    model.fragmentation_restrictions.add( sum(self.model.x[a_idx, t + j] for j in range(min_len)) >= min_len * model.start_block[a_idx, t] )
                if t + max_len < self.number_of_ts:
                    model.fragmentation_restrictions.add( sum(self.model.x[a_idx, t + j] for j in range(max_len + 1)) <= max_len * model.start_block[a_idx, t] )

        # Transition variables for penalty to transition
        model.transition_def = ConstraintList()
        for t in range(1, self.number_of_ts):
            for a in model.activities:
                for b in model.activities:
                    if a != b:
                        model.transition_def.add( model.transition[a, b, t] >= model.x[a, t-1] + model.x[b, t] - 1 )
        
        # Definicion de h_{a,d} = suma de x[a,t] tal que d(t)==d
        model.had_def = ConstraintList()
        for a in model.activities:
            for d in model.days:
                model.had_def.add(model.had[a, d] == sum(model.x[a,t] for t in model.time_slots if day_of(t) == d))
        
        # Definicion h_a = suma h_{ad}
        model.ha_def = ConstraintList()
        for a in model.activities:
            model.ha_def.add(model.ha[a] == sum(model.had[a,d] for d in model.days))

        # Restricciones de h[a, d, k] y y[a, d, k]
        model.segment_logic = ConstraintList()
        for a in model.activities:
            if a not in model.W:
                continue
            for d in model.days:
                K = model.Kad[a, d]
                for k in range(1, K + 1):
                    Hk = model.H[a, d, k]
                    Hk_prev = model.H[a, d, k - 1]
                    model.segment_logic.add(model.h[a, d, k] == sum(
                        model.x[a, t] 
                        for t in model.time_slots 
                        if day_of(t) == d and Hk_prev < sum(model.x[a, tau] for tau in model.time_slots if day_of(tau) == d and tau <= t) <= Hk))
                    model.segment_logic.add(
                        model.h[a, d, k] <= (Hk - Hk_prev) * model.y[a, d, k]
                    )
                    if k > 1:
                        model.segment_logic.add(model.y[a, d, k] <= model.y[a,d,k-1])

        


    def buildModel(self):
        print("Building model...")
        fixedActivities, variableActivities, number_of_ts = self.fixed_activities, self.variable_activities, self.number_of_ts
        # Create model
        model = ConcreteModel()

        # Sets: index from 0 to number_of_ts-1 to match Python lists
        model.T = RangeSet(0, number_of_ts - 1)
        model.D = RangeSet(1, 7)

        # Activity names
        fixed_names = [a.name for a in fixedActivities]
        var_names = [a.name for a in variableActivities]
        all_names = fixed_names + var_names

        model.A = Set(initialize=all_names)
        model.A_F = Set(initialize=fixed_names)
        model.A_V = Set(initialize=var_names)

        # Helper: map time slot to day
        def day_of_t(t):
            blocks_per_day = number_of_ts // 7
            return 1 + (t // blocks_per_day)

        # Decision: x[a,t]
        model.x = Var(model.A, model.T, domain=Binary)

        # Fix fixed activity slots, disable variables outside allowed
        for a in fixedActivities:
            for t in a.assigned_ts:
                if t in model.T:
                    model.x[a.name, t].fix(1)
        for a in variableActivities:
            allowed = set(a.allowed_ts)
            for t in model.T:
                if t not in allowed:
                    model.x[a.name, t].fix(0)

        # Daily hours h[a,d]
        model.h = Var(model.A, model.D, domain=NonNegativeReals)
        def daily_hours_rule(m, a, d):
            return m.h[a, d] == sum(m.x[a, t] for t in m.T if day_of_t(t) == d)
        model.daily_hours = Constraint(model.A, model.D, rule=daily_hours_rule)

        # Total weekly hours Htot[a]
        model.Htot = Var(model.A, domain=NonNegativeReals)
        def total_hours_rule(m, a):
            return m.Htot[a] == sum(m.h[a, d] for d in m.D)
        model.total_hours = Constraint(model.A, rule=total_hours_rule)

        # Bounds on weekly hours for variable activities
        def minmax_weekly_rule(m, a):
            act = next((x for x in variableActivities if x.name == a), None)
            if act:
                return (act.min_ts, m.Htot[a], act.max_ts)
            return Constraint.Skip
        model.weekly_bounds = Constraint(model.A_V, rule=minmax_weekly_rule)

        # Piecewise utility segments setup
        seg_index = []
        H = {}
        u = {}
        for act in variableActivities:
            for d in range(1, 8):
                util = act.utility[d-1]
                K = len(util.utilities_per_segment)
                for k in range(1, K+1):
                    idx = (act.name, d, k)
                    seg_index.append(idx)
                    H[idx] = util.segments[k-1]
                    u[idx] = util.utilities_per_segment[k-1]

        model.SEG = Set(initialize=seg_index, dimen=3)
        model.H = Param(model.SEG, initialize=H)
        model.u = Param(model.SEG, initialize=u)

        # Segment hours and activation
        model.h_seg = Var(model.SEG, domain=NonNegativeReals)
        model.y = Var(model.SEG, domain=Binary)

        def seg_sum_rule(m, a, d):
            return sum(m.h_seg[a, d, k] for (aa, dd, k) in m.SEG if aa == a and dd == d) == m.h[a, d]
        model.seg_sum = Constraint(model.A_V, model.D, rule=seg_sum_rule)

        def seg_bounds_rule(m, a, d, k):
            prev = m.H[a, d, k-1] if k > 1 else 0
            return m.h_seg[a, d, k] <= (m.H[a, d, k] - prev) * m.y[a, d, k]
        model.seg_bounds = Constraint(model.SEG, rule=seg_bounds_rule)

        def y_precedence_rule(m, a, d, k):
            if k == 1:
                return Constraint.Skip
            return m.y[a, d, k] <= m.y[a, d, k-1]
        model.y_prec = Constraint(model.SEG, rule=y_precedence_rule)

        def seg_activation_rule(m, a, d, k):
            if k == 1:
                return Constraint.Skip
            return sum(m.h_seg[a, d, m_] for m_ in range(1, k)) >= m.H[a, d, k] * m.y[a, d, k]
        model.seg_act = Constraint(model.SEG, rule=seg_activation_rule)

        # Define p and its constraints via ConstraintList
        model.p = Var(model.A_V, model.T, domain=Binary)
        model.p_constraints = ConstraintList()
        for a in variableActivities:
            for t in model.T:
                # p >= x - prev
                if t == 0:
                    model.p_constraints.add(model.p[a.name, t] == model.x[a.name, t])
                else:
                    model.p_constraints.add(model.p[a.name, t] >= model.x[a.name, t] - model.x[a.name, t-1])
                    model.p_constraints.add(model.p[a.name, t] <= model.x[a.name, t])
                    model.p_constraints.add(model.p[a.name, t] <= 1 - model.x[a.name, t-1])

        # Adjacent block constraints
        for act in variableActivities:
            for t in model.T:
                if t + act.min_adjacent_ts - 1 in model.T:
                    model.p_constraints.add(
                        model.p[act.name, t] <= sum(model.x[act.name, t+k] for k in range(act.min_adjacent_ts)))
                if t + act.max_adjacent_ts in model.T:
                    model.p_constraints.add(
                        sum(model.x[act.name, t+k] for k in range(act.max_adjacent_ts+1)) <= act.max_adjacent_ts)

        # Transition s
        model.s = Var(model.A, model.A, RangeSet(0, number_of_ts - 2), domain=Binary)
        model.s_constraints = ConstraintList()
        for a in all_names:
            for b in all_names:
                if a == b: continue
                for t in model.T:
                    if t < number_of_ts - 1:
                        model.s_constraints.add(model.s[a, b, t] >= model.x[a, t] + model.x[b, t+1] - 1)
                        model.s_constraints.add(model.s[a, b, t] <= model.x[a, t])
                        model.s_constraints.add(model.s[a, b, t] <= model.x[b, t+1])

        # Objective
        def obj_rule(m):
            util_sum = sum(m.u[a, d, k] * m.h_seg[a, d, k] for (a, d, k) in m.SEG)
            pen_sum = 0
            for act in fixedActivities + variableActivities:
                for b in all_names:
                    if act.name == b: continue
                    pen = act.penalties.get(b, 0)
                    for t in model.T:
                        if t < number_of_ts - 1:
                            pen_sum += pen * m.s[act.name, b, t]
            return util_sum - pen_sum
        model.obj = Objective(rule=obj_rule, sense=maximize)

        print("Done!")
        return model                    



    def solve(self):
        print("Solving...")
            # Dummy solve output: Replace with actual solver logic
        return (123.45, {(1, 30): 1})