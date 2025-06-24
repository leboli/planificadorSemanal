from entities.activity import activity
class fixedActivity(activity):
    def __init__(self, name: str, penalties: dict, assigned_ts: list):
        super().__init__(name, penalties)
        self.__assigned_ts = assigned_ts

    @property
    def assigned_ts(self):
        return self.__assigned_ts

    @assigned_ts.setter
    def assigned_ts(self, value: list):
        self.__assigned_ts = value
