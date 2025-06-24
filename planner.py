from pyomo.environ import *

class planner():
    def __init__(self, fixed_activities, variable_activities, number_of_ts):
        self.fixed_activities = fixed_activities  # list of fixedActivity
        self.variable_activities = variable_activities  # list of variableActivity
        self.number_of_ts = number_of_ts  # total number of time slots in the schedule (e.g., 168 = 1 week in hours)
        self.model = ConcreteModel()

    def buildModel(self):
        print("Building model...")

        self.model = ConcreteModel()

        # Sets: total activities and time slots
        num_fixed = len(self.fixed_activities)
        num_variable = len(self.variable_activities)
        total_activities = num_fixed + num_variable
        time_slots = range(self.number_of_ts)

        self.model.activities = Set(initialize=range(total_activities))
        self.model.time_slots = Set(initialize=time_slots)

        # Binary variable x[a, t]: 1 if activity a is assigned to time slot t
        self.model.x = Var(self.model.activities, self.model.time_slots, domain=Binary)

        # --- Fix assignment for fixed activities ---
        for index, fixed in enumerate(self.fixed_activities):
            for t in fixed.assigned_ts:
                self.model.x[index, t].fix(1)

        # --- Prevent variable activities from being scheduled in disallowed slots ---
        for index, variable in enumerate(self.variable_activities):
            var_idx = num_fixed + index
            for t in time_slots:
                if t not in variable.allowed_ts:
                    self.model.x[var_idx, t].fix(0)

        # --- Constraint: at most one activity per time slot ---
        def one_per_slot_rule(m, t):
            return sum(m.x[a, t] for a in m.activities) <= 1
        self.model.one_activity_per_slot = Constraint(self.model.time_slots, rule=one_per_slot_rule)

        # --- Min/Max time slots per variable activity ---
        self.model.min_constraints = ConstraintList()
        self.model.max_constraints = ConstraintList()

        for index, variable in enumerate(self.variable_activities):
            a_idx = num_fixed + index
            self.model.min_constraints.add(
                sum(self.model.x[a_idx, t] for t in time_slots) >= variable.min_slots
            )
            self.model.max_constraints.add(
                sum(self.model.x[a_idx, t] for t in time_slots) <= variable.max_slots
            )

        # --- Fragmentation constraints (min/max block size per activity) ---
        self.model.fragmentation_restrictions = ConstraintList()
        self.model.start_block = Var(self.model.activities, self.model.time_slots, domain=Binary)

        for index, variable in enumerate(self.variable_activities):
            a_idx = num_fixed + index
            min_len = variable.min_adjacent_ts
            max_len = variable.max_adjacent_ts

            for t in time_slots:
                if t + min_len <= self.number_of_ts:
                    self.model.fragmentation_restrictions.add(
                        sum(self.model.x[a_idx, t + j] for j in range(min_len)) >=
                        min_len * self.model.start_block[a_idx, t]
                    )
                if t + max_len <= self.number_of_ts:
                    self.model.fragmentation_restrictions.add(
                        sum(self.model.x[a_idx, t + j] for j in range(max_len + 1)) <=
                        max_len * self.model.start_block[a_idx, t]
                    )

        # --- Transition variables (to model penalties between activities) ---
        self.model.transition = Var(self.model.activities, self.model.activities, self.model.time_slots, domain=Binary)
        self.model.transition_def = ConstraintList()

        for t in range(1, self.number_of_ts):
            for a in self.model.activities:
                for b in self.model.activities:
                    if a != b:
                        self.model.transition_def.add(
                            self.model.transition[a, b, t] >= self.model.x[a, t-1] + self.model.x[b, t] - 1
                        )

        # --- Auxiliary variables for piecewise utility ---
        max_segments = max(len(var.utility.utility_segments[d]) for var in self.variable_activities for d in range(7))
        self.model.h_adk = Var(range(num_variable), range(7), range(max_segments), domain=NonNegativeReals)

        # --- Build penalty matrix dynamically ---
        penalties = dict()
        for i, act_i in enumerate(self.variable_activities):
            a_idx = num_fixed + i
            for j, act_j in enumerate(self.variable_activities):
                b_idx = num_fixed + j
                if a_idx != b_idx:
                    value = act_i.penalty.get(act_j.name, 0)
                    penalties[(a_idx, b_idx)] = value

        # --- Objective function: maximize utility - transition penalty ---
        def objective_rule(m):
            total_utility = 0
            total_penalty = 0

            for a_idx, var_act in enumerate(self.variable_activities):
                for d in range(7):
                    segments = var_act.utility.utility_segments[d]
                    for k, (start, end, util) in enumerate(segments):
                        total_utility += util * m.h_adk[a_idx, d, k]

            for (a, b), penalty_val in penalties.items():
                for t in m.time_slots:
                    total_penalty += penalty_val * m.transition[a, b, t]

            return total_utility - total_penalty

        self.model.obj = Objective(rule=objective_rule, sense=maximize)

    def solve(self):
        print("Solving...")
        # Dummy solve output: Replace with actual solver logic
        return (123.45, {(1, 30): 1})