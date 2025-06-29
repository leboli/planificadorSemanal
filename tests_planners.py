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
        fixedActivity("Class", assigned_ts=[t for t in range(48)], penalties={})
    ]

    utility_example = [dailyUtility(
        segments=[2, 12, 24],
        utilities_per_segment=[8, t, 2]
    ) for t in range(7)]

    gymac = variableActivity(
        name="Gym",
        utility=utility_example,
        min_ts=2,
        max_ts=4,
        allowed_ts=[0, 1, 4, 5, 6, 7],
        min_adjacent_ts=1,
        max_adjacent_ts=2,
        penalty={}
    )
    readac = variableActivity(
        name="Reading",
        utility=utility_example,
        min_ts=2,
        max_ts=3,
        allowed_ts=[1, 4, 5, 6],
        min_adjacent_ts=1,
        max_adjacent_ts=2,
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
                print(f"Activity '{a}' scheduled at time slot {t}")
    else:
        print("Solver did not find an optimal solution.")