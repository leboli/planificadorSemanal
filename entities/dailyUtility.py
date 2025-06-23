class dailyUtility():

    def __init__(self, segments:list[int], utilities_per_segment:list[float]):
        
        self.__segments = segments                              #H_{a,d,k}
        self.__utilities_per_segment = utilities_per_segment    #u_{a,d,k}
        

    # segments
    @property
    def segments(self):
        return self.__segments
    
    @segments.setter
    def segments(self, value:str):
        self.__segments = value

    # utilities
    @property
    def utilities_per_segment(self):
        return self.__utilities_per_segment
    
    @utilities_per_segment.setter
    def utilities_per_segment(self, value:list):
        self.__utilities_per_segment = value