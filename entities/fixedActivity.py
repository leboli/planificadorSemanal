class fixedActivity():

    def __init__(self, name:str, assigned_ts:list):
        self.__name = name

        # This list contains the indexes from the week time slots this activity requires 
        self.__assigned_ts = assigned_ts

    # name
    @property
    def name(self):
        return self.__name
    
    @name.setter
    def name(self, value:str):
        self.__name = value

    # time slots
    @property
    def assigned_ts(self):
        return self.__assigned_ts
    
    @assigned_ts.setter
    def assigned_ts(self, value:list):
        self.__assigned_ts = value