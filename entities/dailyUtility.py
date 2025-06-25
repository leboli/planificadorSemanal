class dailyUtility():

    def __init__(self, segments:list[int], utilities_per_segment:list[float]):
        
        self.__segments = segments                              #H_{a,d,k}
        self.__utilities_per_segment = utilities_per_segment    #u_{a,d,k}
        
    def __str__(self):
        parts = []
        start = 0
        # iterate over each segment end and its utility
        for end, util in zip(self.segments, self.utilities_per_segment):
            parts.append(f"{start}-{end}:{util}")
            start = end
        # if there's one more utility after the last segment, include it to end-of-day
        if len(self.utilities_per_segment) > len(self.segments):
            util = self.utilities_per_segment[-1]
            parts.append(f"{start}-   :{util}")
        return ", ".join(parts)

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

