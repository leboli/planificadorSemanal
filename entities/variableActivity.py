from utility import Utility

class VariableActivity():

    def __init__(self, name:str, utility:Utility, minimum_hours:int, maximum_hours:int, allowed_time_slot:list, min_adjacent_ts:int, max_adjacent_ts:int, penalty:dict):
        self.__name = name
        self.__utility = utility

        # Maximum and mmum hours to dedicate to this activity
        # Son unidades de tiempo, segun lo seleccionado (168, 336, 672)
        self.__minimum_hours = minimum_hours 
        self.__maximum_hours = maximum_hours

        # List format: [beginning_mon_ts, ending_mon_ts, beginning_tue_ts, ...]
        # The list has a fixed length of 14 elements, each pair corresponding to the beginning of the
        # time slot allowed and the ending.
        self.__allowed_time_slot = allowed_time_slot

        # To limit excesive fragmentation or long blocks for an activity we define:
        self.__min_adjacent_ts = min_adjacent_ts # minimum amount of adjacent time slots
        self.__max_adjacent_ts = max_adjacent_ts # maximum amount of adjacent time slots
        
        # Penalty to transition to this activity to another
        # Keys: The other activity
        # Value: penalty
        self.__penalty_to_transition = penalty

     # name
    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value:str):
        self.__name = value

    # utility
    @property
    def utility(self):
        return self.__utility

    @utility.setter
    def utility(self, value:Utility):
        self.__utility = value

    # minimum_hours
    @property
    def minimum_hours(self):
        return self.__minimum_hours

    @minimum_hours.setter
    def minimum_hours(self, value:int):
        self.__minimum_hours = value

    # maximum_hours
    @property
    def maximum_hours(self):
        return self.__maximum_hours

    @maximum_hours.setter
    def maximum_hours(self, value:int):
        self.__maximum_hours = value

    # allowed_time_slot
    @property
    def allowed_time_slot(self):
        return self.__allowed_time_slot

    @allowed_time_slot.setter
    def allowed_time_slot(self, value:list):
        self.__allowed_time_slot = value

    # min_adjacent_ts
    @property
    def min_adjacent_ts(self):
        return self.__min_adjacent_ts

    @min_adjacent_ts.setter
    def min_adjacent_ts(self, value:int):
        self.__min_adjacent_ts = value

    # max_adjacent_ts
    @property
    def max_adjacent_ts(self):
        return self.__max_adjacent_ts

    @max_adjacent_ts.setter
    def max_adjacent_ts(self, value:int):
        self.__max_adjacent_ts = value

    # penalty_to_transition
    @property
    def penalty_to_transition(self):
        return self.__penalty_to_transition

    @penalty_to_transition.setter
    def penalty_to_transition(self, value:dict):
        self.__penalty_to_transition = value