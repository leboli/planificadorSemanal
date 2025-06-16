class Utility():

    def __init__(self, monday:dict, tuesday:dict, wednesday:dict, thursday:dict, friday:dict, saturday:dict, sunday:dict):

        # Each of these variables is a dictionary, whose keys represent the blocks of hours into which the day is divided. 
        # The items are the utility assigned to each block.
    
        self.__monday = monday
        self.__tuesday = tuesday
        self.__wednesday = wednesday
        self.__thursday = thursday
        self.__friday = friday
        self.__saturday = saturday
        self.__sunday = sunday

    @property
    def monday(self):
        return self.__monday

    @monday.setter
    def monday(self, value:dict):
        self.__monday = value

    @property
    def tuesday(self):
        return self.__tuesday

    @tuesday.setter
    def tuesday(self, value:dict):
        self.__tuesday = value

    @property
    def wednesday(self):
        return self.__wednesday

    @wednesday.setter
    def wednesday(self, value:dict):
        self.__wednesday = value

    @property
    def thursday(self):
        return self.__thursday

    @thursday.setter
    def thursday(self, value:dict):
        self.__thursday = value

    @property
    def friday(self):
        return self.__friday

    @friday.setter
    def friday(self, value:dict):
        self.__friday = value

    @property
    def saturday(self):
        return self.__saturday

    @saturday.setter
    def saturday(self, value:dict):
        self.__saturday = value

    @property
    def sunday(self):
        return self.__sunday

    @sunday.setter
    def sunday(self, value:dict):
        self.__sunday = value

