from entities.fixedActivity import fixedActivity
from entities.variableActivity import variableActivity
from entities.dailyUtility import dailyUtility
from entities.activity import Activity
from planner import planner

from pyomo.opt import SolverFactory
from pyomo.environ import value


if __name__ == "__main__":

    fixed_activities = [
        fixedActivity("Class", assigned_ts=[2, 3], penalties={})
    ]

    utility_example = dailyUtility(
        segments=[2, 3, 2],
        utilities_per_segment=[8, 5, 2]
    )


    variable_activities = [
        variableActivity(
            name="Gym",
            utility=utility_example,
            min_ts=2,
            max_ts=4,
            allowed_ts=[0, 1, 4, 5, 6, 7],
            min_adjacent_ts=1,
            max_adjacent_ts=2,
            penalty={"Reading": 3}
        ),
        variableActivity(
            name="Reading",
            utility=utility_example,
            min_ts=2,
            max_ts=3,
            allowed_ts=[1, 4, 5, 6],
            min_adjacent_ts=1,
            max_adjacent_ts=2,
            penalty={"Gym": 2}
        )
    ]

    plan = planner(fixed_activities, variable_activities, number_of_ts=168)
    plan.buildModel()

    # Use GLPK solver (must be installed and accessible in PATH)
    solver = SolverFactory('glpk')
    result = solver.solve(plan.model, tee=True)

    # Print some results
    print("Objective value:", plan.model.obj())
    for (a, t) in plan.model.x:
        if value(plan.model.x[a, t]) > 0.5:
            print(f"Activity {a} scheduled at time slot {t}")
