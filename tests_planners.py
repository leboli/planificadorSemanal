from entities.fixedActivity import fixedActivity
from entities.variableActivity import variableActivity
from entities.dailyUtility import dailyUtility
from entities.activity import activity
from planner import planner

from pyomo.opt import SolverFactory
from pyomo.environ import value


if __name__ == "__main__":

    # C:\Program Files (x86)\winglpk-4.65\glpk-4.65\w64

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
            penalty={gymac: 2}
        )

    variable_activities = [
        gymac,
        readac
    ]

    plan = planner(fixed_activities, variable_activities, number_of_ts=168)
    model = plan.buildModel()

    results = SolverFactory('glpk').solve(model)
    results.write()
    if results.solver.status == 'ok':
        model.pprint()

    # Print some results
    print("Objective value:", model.obj())
    for (a, t) in model.x:
        if value(model.x[a, t]) > 0.5:
            print(f"Activity {a} scheduled at time slot {t}")