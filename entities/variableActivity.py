from entities.dailyUtility import dailyUtility
from entities.activity import activity

class variableActivity(activity):
    def __init__(self, name: str, utility, min_ts: int, max_ts: int,
                 allowed_ts: list, min_adjacent_ts: int, max_adjacent_ts: int,
                 penalty: dict):
        super().__init__(name, penalty)
        self.__utility = utility
        self.__min_ts = min_ts
        self.__max_ts = max_ts
        self.__allowed_ts = allowed_ts
        self.__min_adjacent_ts = min_adjacent_ts
        self.__max_adjacent_ts = max_adjacent_ts

    @property
    def utility(self):
        return self.__utility

    @utility.setter
    def utility(self, value):
        self.__utility = value

    @property
    def min_ts(self):
        return self.__min_ts

    @min_ts.setter
    def min_ts(self, value: int):
        self.__min_ts = value

    @property
    def max_ts(self):
        return self.__max_ts

    @max_ts.setter
    def max_ts(self, value: int):
        self.__max_ts = value

    @property
    def allowed_ts(self):
        return self.__allowed_ts

    @allowed_ts.setter
    def allowed_ts(self, value: list):
        self.__allowed_ts = value

    @property
    def min_adjacent_ts(self):
        return self.__min_adjacent_ts

    @min_adjacent_ts.setter
    def min_adjacent_ts(self, value: int):
        self.__min_adjacent_ts = value

    @property
    def max_adjacent_ts(self):
        return self.__max_adjacent_ts

    @max_adjacent_ts.setter
    def max_adjacent_ts(self, value: int):
        self.__max_adjacent_ts = value


   