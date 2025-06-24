from entities.dailyUtility import dailyUtility
from entities.activity import Activity

class variableActivity(Activity):

    def __init__(self, name:str, utility:dailyUtility, min_ts:int, max_ts:int, allowed_ts:list, min_adjacent_ts:int, max_adjacent_ts:int, penalty:dict):
        super().__init__(name, penalty)
        self.__utility = utility

        # Maximum and minimum hours to dedicate to this activity
        # Son unidades de tiempo, segun lo seleccionado (168, 336, 672)
        self.__min_ts = min_ts 
        self.__max_ts = max_ts

        # List format: [beginning_mon_ts, ending_mon_ts, beginning_tue_ts, ...]
        # The list has a fixed length of 14 elements, each pair corresponding to the beginning of the
        # time slot allowed and the ending.
        self.__allowed_ts = allowed_ts

        # To limit excesive fragmentation or long blocks for an activity we define:
        self.__min_adjacent_ts = min_adjacent_ts # minimum amount of adjacent time slots
        self.__max_adjacent_ts = max_adjacent_ts # maximum amount of adjacent time slots
        


    # utility
    @property
    def utility(self):
        return self.__utility

    @utility.setter
    def utility(self, value:dailyUtility):
        self.__utility = value

    # minimum_hours
    @property
    def min_ts(self):
        return self.__min_ts

    @min_ts.setter
    def min_ts(self, value:int):
        self.__min_ts = value

    # maximum_hours
    @property
    def max_ts(self):
        return self.__max_ts

    @max_ts.setter
    def max_ts(self, value:int):
        self.__max_ts = value

    # allowed_time_slot
    @property
    def allowed_ts(self):
        return self.__allowed_ts

    @allowed_ts.setter
    def allowed_ts(self, value:list):
        self.__allowed_ts = value

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


    def set_constant_utility(self, utility):
        for d in range(1,8):
            self.utility[d] = dailyUtility([24], [utility])

    def set_daily_utility(self, day, segments, utils):
        self.utility[day] = dailyUtility(segments, utils)