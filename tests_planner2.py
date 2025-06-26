from entities.fixedActivity import fixedActivity
from entities.variableActivity import variableActivity
from entities.dailyUtility import dailyUtility
from planner import planner

from pyomo.opt import SolverFactory
from pyomo.environ import value, TerminationCondition


if __name__ == "__main__":

    # RUTA ABSOLUTA A glpsol, si no está en PATH
    glpsol_path = r"C:\Program Files (x86)\winglpk-4.65\glpk-4.65\w64\glpsol.exe"
    
    Test1 = False
    if Test1:
        fixed_activities = [
            fixedActivity("Class", assigned_ts=[7,8,9,10,11,12,31,32,33,34,35,36,55,56,57,58,59,60,79,80,81,82,83,84,103,104,105,106], penalties={})
        ]

        utility_example = [dailyUtility(
            segments=[8, 12, 20, 24],
            utilities_per_segment=[-3, 4, 6, 2]
        ) for _ in range(7)]

        gymac = variableActivity(
            name="Gym",
            utility=utility_example,
            min_ts=13,
            max_ts=90,
            allowed_ts=[t for t in range(1,169)],
            min_adjacent_ts=1,
            max_adjacent_ts=2,
            penalty={}
        )
        readac = variableActivity(
            name="Study",
            utility=utility_example,
            min_ts=15,
            max_ts=40,
            allowed_ts=[n for n in range(168)],
            min_adjacent_ts=2,
            max_adjacent_ts=6,
            penalty={gymac.name: 2}
        )

        variable_activities = [
            gymac,
            readac
        ]
    else:
        fixed_activities=[fixedActivity("test",[t for t in range(1,168)],{})]
        #variable_activities=[variableActivity("test",[dailyUtility([6,24],[-3,10]) for _ in range(7)],43,168,[t for t in range(1,169)],1,168,{})]
        variable_activities=[]



    plan = planner(fixed_activities, variable_activities, number_of_ts=168)
    model = plan.buildModel()

    # Seleccionar solver GLPK
    solver = SolverFactory('glpk', executable=glpsol_path)
    results = solver.solve(model, tee=True)
    results.write()

    # Comprobar estado y condición óptima
    if (results.solver.status == 'ok' and
        results.solver.termination_condition == TerminationCondition.optimal):
        # Imprimir resumen del modelo y solución
        print("\n=== Solution Summary ===")
        print(f"Objective = {value(model.obj)}\n")
        for (a, t) in model.x:
            if value(model.x[a, t]) > 0.5:
                print(f"Activity '{a}' scheduled at time slot {t} ---> h {t%24}")
    else:
        print("Solver did not find an optimal solution.")

    if False:
        print("=============================================================================================" \
    "==============================================================================================")
        print("\n" + "="*40)
        print(" MODEL DEBUG DUMP ")
        print("="*40 + "\n")

        # 1) Objective
        print(">> Objective expression:")
        print("   ", model.obj.expr)
        print(">> Objective value:", value(model.obj), "\n")

        # 2) Piecewise parameters H and u
        print(">> Piecewise parameters (H bounds and u utilities):")
        for (a,d,k) in sorted(model.SEG):
            print(f"   Activity={a}, Day={d}, Segment={k} → H={model.H[a,d,k]}, u={model.u[a,d,k]}")
        print()

        # 3) Slot assignment x[a,t]
        print(">> Slot assignments x[a,t] (1 = assigned):")
        for a in model.A:
            assigned = [t for t in model.T if value(model.x[a,t]) >= 0.5]
            print(f"   {a}: slots = {assigned}")
        print()

        # 4) Daily and weekly loads
        print(">> Daily loads h[a,d] and weekly totals Htot[a]:")
        for a in model.A:
            print(f"   Activity {a}:")
            for d in model.D:
                hd = value(model.h[a,d])
                print(f"      Day {d}: h = {hd}")
            Ht = value(model.Htot[a])
            print(f"      Weekly Htot = {Ht}\n")

        # 5) Segment variables h_seg and y
        print(">> Segment allocations h_seg[a,d,k] and activation y[a,d,k]:")
        for (a,d,k) in sorted(model.SEG):
            hsk = value(model.h_seg[a,d,k])
            ysk = value(model.y[a,d,k])
            print(f"   {a}, Day {d}, segment {k}: h_seg = {hsk}, y = {ysk}")
        print()

        # 6) Contiguous‐block indicators p[a,t]
        print(">> Block starts p[a,t]:")
        for a in model.A_V:
            starts = [t for t in model.T if value(model.p[a,t]) >= 0.5]
            print(f"   {a} starts at slots: {starts}")
        print()

        # 7) Transitions s[a,b,t]
        print(">> Transitions s[a,b,t] (1 = a→b between t→t+1):")
        for a in model.A:
            for b in model.A:
                if a == b:
                    continue
                trans = [t for t in model.T if t < model.T.last() and value(model.s[a,b,t]) >= 0.5]
                if trans:
                    print(f"   {a}→{b} at slots: {trans}")
        print()

        # 8) Penalties actually incurred
        print(">> Penalty contributions per (a,b,t):")
        total_pen = 0
        for act in fixed_activities + variable_activities:
            for other in model.A:
                if other == act.name:
                    continue
                val = act.penalties.get(other, 0)
                if val == 0:
                    continue
                for t in model.T:
                    if t < model.T.last():
                        st = value(model.s[act.name, other, t])
                        if st >= 0.5:
                            contrib = val * st
                            total_pen += contrib
                            print(f"   Penalty {act.name}→{other} at t={t}: rate={val}, value={contrib}")
        print(f"   Total penalty = {total_pen}\n")

        # 9) Utility contributions by segment
        print(">> Utility contributions by segment h_seg * u:")
        total_util = 0
        for (a,d,k) in sorted(model.SEG):
            hsk = value(model.h_seg[a,d,k])
            uval = value(model.u[a,d,k])
            contrib = hsk * uval
            total_util += contrib
            print(f"   {a}, Day {d}, seg {k}: h_seg={hsk}, u={uval}, contrib={contrib}")
        print(f"   Total utility = {total_util}\n")

        print("="*40 + " END DEBUG " + "="*40 + "\n")


