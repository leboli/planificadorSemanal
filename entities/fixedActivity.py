class FixedActivity():

    def __init__(self, name:str, time_slots:list):
        self.__name = name

        # This list contains the indexes from the week time slots this activity requires 
        self.__time_slots = time_slots

    # name
    @property
    def name(self):
        return self.__name
    
    @name.setter
    def name(self, value:str):
        self.__name = value

    # time slots
    @property
    def time_slots(self):
        return self.time_slots
    
    @time_slots.setter
    def time_slots(self, value:list):
        self.__time_slots = value