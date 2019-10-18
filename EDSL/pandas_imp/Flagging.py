import json


class Flag:
    def __init__(self):
        self.config = "Flagging_Config.json"
        self.flagCodes = self.fetchFlagConfig();

    def fetchFlagConfig(self):
        # insert reading and parsing of flag configuration
        flagCodes = {'None':'0', 'Basic Outlier Test':'1', 'Repeat Value Test':'2', 'Spatial Inconsistency':'3', 'Machine Learning':'4'};

        with open(self.config, 'r') as F:
            flagCodes = json.load(F)

        return flagCodes;

    def returnGoodFlag(self):
        return self.flagCodes['None']

    def flag(self, failed, test):
        if(not failed):
            try:
                return self.flagCodes[test]
            except KeyError:
                print('''Exception raised from flagging class:
    Test name not defined in flag codes.
    Please check your spelling on test names and/or verify that the flag code was defined in the configuration file.''')
                return(None)
        else:
            return self.flagCodes['None']
