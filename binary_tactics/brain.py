class brain():
    #use pyneurgen
    def __init__(self):
        self.network = None
        self.fitness = None
        self.unit    = None
        self.gridsize = None
        self.location = None
        
        """
        The fittness function will be tricky,
        for each action it will know what the result was.
        and it will know which inputs and outputs contributed to that action
        """
        
        #inputs
        self.eyes = None #see what's on the field, find targets
        self.nose = None #smell unit/stone composition
        
        #outputs
        self.feet = None #move to target
        self.mouth = None #attack targets, imbue/eat targets
        