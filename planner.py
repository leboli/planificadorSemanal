from pyomo.environ import *
import os

class planner():
    def __init__(self, fixed_activities, variable_activities, number_of_ts):
        self.fixed_activities = fixed_activities  # list of fixedActivity
        self.variable_activities = variable_activities  # list of variableActivity
        self.number_of_ts = number_of_ts  # total number of time slots in the schedule (e.g., 168 = 1 week in hours)      


    def buildModel(self):
        fixedActivities = self.fixed_activities
        variableActivities = self.variable_activities
        N = self.number_of_ts

        model = ConcreteModel()
        # Sets
        model.T = RangeSet(0, N-1)
        model.D = RangeSet(1,7)
        fixed_names = [a.name for a in fixedActivities]
        var_names = [a.name for a in variableActivities]
        all_names = fixed_names + var_names
        model.A = Set(initialize=all_names)
        model.A_F = Set(initialize=fixed_names)
        model.A_V = Set(initialize=var_names)

        # helper day mapping
        def day_of_t(t):
            return 1 + (t // (N//7))

        # x[a,t]
        model.x = Var(model.A, model.T, domain=Binary)
        # at most one activity per slot
        model.one_per_t = Constraint(model.T, rule=lambda m,t: sum(m.x[a,t] for a in m.A) <= 1)

        # fix fixed slots
        for a in fixedActivities:
            for t in a.assigned_ts:
                if 0 <= t < N:
                    model.x[a.name,t].fix(1)
        # forbid outside allowed
        for a in variableActivities:
            allowed = set(a.allowed_ts)
            for t in model.T:
                if t not in allowed:
                    model.x[a.name,t].fix(0)

        # daily and total hours
        model.h = Var(model.A, model.D, domain=NonNegativeReals)
        model.daily = Constraint(model.A, model.D, rule=lambda m,a,d: m.h[a,d]==sum(m.x[a,t] for t in m.T if day_of_t(t)==d))
        model.Htot = Var(model.A, domain=NonNegativeReals)
        model.weekly = Constraint(model.A, rule=lambda m,a: m.Htot[a]==sum(m.h[a,d] for d in m.D))
        # bounds
        def weekly_bounds_min(m,a):
            act = next(act for act in variableActivities if act.name==a)
            return m.Htot[a] >= act.min_ts
        def weekly_bounds_max(m,a):
            act = next(act for act in variableActivities if act.name==a)
            return m.Htot[a] <= act.max_ts

        model.weekly_min = Constraint(model.A_V, rule=weekly_bounds_min)
        model.weekly_max = Constraint(model.A_V, rule=weekly_bounds_max)


        # piecewise segments
        segs=[];H={};U={}
        for act in variableActivities:
            for d in model.D:
                util=act.utility[d-1]
                for k,(seg,uval) in enumerate(zip(util.segments,util.utilities_per_segment),start=1):
                    segs.append((act.name,d,k)); H[act.name,d,k]=seg; U[act.name,d,k]=uval
        model.SEG=Set(initialize=segs,dimen=3)
        model.H=Param(model.SEG,initialize=H)
        model.u=Param(model.SEG,initialize=U)

        model.h_seg=Var(model.SEG,domain=NonNegativeReals)
        model.y=Var(model.SEG,domain=Binary)
        # segment sum
        model.seg_sum=Constraint(model.A_V,model.D,rule=lambda m,a,d: sum(m.h_seg[a,d,k] for (aa,dd,k) in m.SEG if aa==a and dd==d)==m.h[a,d])
        # bounds and precedence
        def seg_bound(m,a,d,k): return m.h_seg[a,d,k]<=(m.H[a,d,k] - (m.H[a,d,k-1] if k>1 else 0))*m.y[a,d,k]
        model.seg_bound=Constraint(model.SEG,rule=seg_bound)
        model.seg_prec=Constraint(model.SEG,rule=lambda m,a,d,k: Constraint.Skip if k==1 else m.y[a,d,k]<=m.y[a,d,k-1])
        def seg_act(m, a, d, k):
            # Para k=1 no hay activación previa
            if k == 1:
                return Constraint.Skip
            # k>1: el tramo k solo puede activarse si
            #   sum_{m=1}^{k-1} h_seg[a,d,m] >= H[a,d,k-1] * y[a,d,k]
            return sum(m.h_seg[a, d, m_] for m_ in range(1, k)) \
                >= m.H[a, d, k-1] * m.y[a, d, k]

        model.seg_act = Constraint(model.SEG, rule=seg_act)

        # block start p
        model.p=Var(model.A_V,model.T,domain=Binary)
        model.pcon=ConstraintList()
        for act in variableActivities:
            Lmin=act.min_adjacent_ts; Lmax=act.max_adjacent_ts
            for t in model.T:
                # define p
                if t==0: model.pcon.add(model.p[act.name,t]==model.x[act.name,t])
                else:
                    model.pcon.add(model.p[act.name,t]>=model.x[act.name,t]-model.x[act.name,t-1])
                    model.pcon.add(model.p[act.name,t]<=model.x[act.name,t])
                    model.pcon.add(model.p[act.name,t]<=1-model.x[act.name,t-1])
                # min contiguous: p=> next Lmin x=1
                for k in range(Lmin):
                    if t+k in model.T: model.pcon.add(model.p[act.name,t]<=model.x[act.name,t+k])
                # max contiguous
                if t + Lmax - 1 < N:  
                    model.pcon.add(sum(model.x[act.name, t+k] for k in range(Lmax)) <= Lmax)


        # transitions s
        model.s=Var(model.A,model.A,RangeSet(0,N-2),domain=Binary)
        model.scon=ConstraintList()
        for a in all_names:
            for b in all_names:
                if a==b: continue
                for t in model.T:
                    if t< N-1:
                        model.scon.add(model.s[a,b,t]>=model.x[a,t]+model.x[b,t+1]-1)
                        model.scon.add(model.s[a,b,t]<=model.x[a,t])
                        model.scon.add(model.s[a,b,t]<=model.x[b,t+1])

        # objective
        def obj_rule(m):
            util = sum(m.u[a,d,k] * m.h_seg[a,d,k] for (a,d,k) in m.SEG)
            pen  = sum(
                act.penalties.get(b,0) * m.s[act.name,b,t]
                for act in fixedActivities + variableActivities
                for b in m.A if b != act.name
                for t in m.T if t < N-1
            )
            return util - pen

        model.obj = Objective(rule=obj_rule, sense=maximize)

        return model                    



    def solve(self, tolerance):
        print("Solving...")
        glpsol_path = os.environ.get("GLPSOL_PATH", "glpsol")
        
        model = self.buildModel()
        # Select the solver
        solver = SolverFactory('glpk', executable=glpsol_path)
        solver.options['mipgap'] = tolerance
        results = solver.solve(model, tee=True)
        results.write()

        # Check state and optimal condition
        if ( results.solver.status == 'ok'
            and results.solver.termination_condition
                in (TerminationCondition.optimal,
                    TerminationCondition.feasible) ):

            # Provide the optimal solution
            solution = ([value(model.obj)],[None]*self.number_of_ts)

            for (a,t) in model.x:
                if value(model.x[a,t]) > 0.5:
                    solution[1].pop(t-1)
                    solution[1].insert(t-1,a)

            # Print model and solution
            print("\n=== Solution Summary ===")
            print(f"Objective = {value(model.obj)}\n")
            for (a, t) in model.x:
                if value(model.x[a, t]) > 0.5:
                    print(f"Activity '{a}' scheduled at time slot {t} ---> h {t%24}")

            return solution

        else:
            print("Solver did not find an optimal solution.")
            return None