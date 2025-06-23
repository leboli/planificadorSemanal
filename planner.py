from entities import fixedActivity
from entities import dailyUtility
from entities import variableActivity

class planner():

    def __init__(self, fixed_activities:list, variable_activities:list, number_of_ts:int):

        self.fixed_activities = fixed_activities
        self.variable_activities = variable_activities



    def buildModel():
        
        print("Build model called.")

        
    def solve():

        print("solve called.")
        return (123.45,{(1,30):1}) #(utility, dict of all x_{a,t})