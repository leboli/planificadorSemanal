from entities import fixedActivity
from entities import dailyUtility
from entities import variableActivity

from pyomo.environ import *

class planner():

    def __init__(self, fixed_activities:list, variable_activities:list, number_of_ts:int):

        self.fixed_activities = fixed_activities
        self.variable_activities = variable_activities
        self.number_of_ts = number_of_ts
        self.model = ConcreteModel()



    def buildModel(self):
    
        print("Build model called.")

        activities = list(range(len(self.fixed_activities) + len(self.variable_activities)))
        time_slots = list(range(self.number_of_ts))

        self.model.x = Var(activities, time_slots, domain = Binary)

        # Fix the fixed activities
        for index, fixed_activity in enumerate(self.fixed_activities):
            for t in fixed_activity.assigned_ts:
                self.model.x[index, t].fix(1)

        # Sets as 0 the not allowed time solt for each variable activity
        var_offset = len(self.fixed_activities)
        for index2, variable_activity in enumerate(self.variable_activities):
            for t in time_slots:
                if t not in variable_activity.allowed_ts:
                    self.model.x[var_offset + index2, t].fix(0)
        
        


        
    def solve():

        print("solve called.")
        return (123.45,{(1,30):1}) #(utility, dict of all x_{a,t})