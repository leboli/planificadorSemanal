from entities import fixedActivity
from entities import utility
from entities import variableActivity

class Planner():

    def __init__(self, number_of_ts:int):

        self.fixed_activities = []
        self.variable_activities = []
        self.time_slots = [None]*number_of_ts
