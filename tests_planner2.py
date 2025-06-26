from entities.fixedActivity import fixedActivity
from entities.variableActivity import variableActivity
from entities.dailyUtility import dailyUtility
from planner import planner

from pyomo.opt import SolverFactory
from pyomo.environ import value, TerminationCondition


if __name__ == "__main__":

    # RUTA ABSOLUTA A glpsol, si no está en PATH
    glpsol_path = r"C:\Program Files (x86)\winglpk-4.65\glpk-4.65\w64\glpsol.exe"

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
        min_ts=5,
        max_ts=8,
        allowed_ts=[14,15,16,17,18,19,20,21,38,39,40,61,62,63,64,65,66,67,68,69,70,71,72,73,74,90,91,92,108,109,110,111],
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

    plan2 = planner(fixed_activities, variable_activities, number_of_ts=168)
    print(plan2.solve())