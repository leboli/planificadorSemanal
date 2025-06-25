from entities.activity import activity

class fixedActivity(activity):

    def __init__(self, name:str, assigned_ts:list, penalties:dict):
        super().__init__(name, penalties)

        # This list contains the indexes from the week time slots this activity requires 
        self.__assigned_ts = assigned_ts


    # time slots
    @property
    def assigned_ts(self):
        return self.__assigned_ts
    
    @assigned_ts.setter
    def assigned_ts(self, value:list):
        self.__assigned_ts = value

    def __str__(self):
        return self.name + " " + str(self.assigned_ts) + " " + str(self.penalties) 