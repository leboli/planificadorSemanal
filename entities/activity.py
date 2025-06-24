from abc import ABC

class Activity(ABC):

    def __init__(self, name:str, penalties:dict):
        self.__name = name
        self.__penalties = penalties

    # name
    @property
    def name(self):
        return self.__name
    
    @name.setter
    def name(self, value:str):
        self.__name = value

    # penalty_to_transition
    @property
    def penalties(self):
        return self.__penalties

    @penalties.setter
    def penalties(self, value:dict):
        self.__penalties = value