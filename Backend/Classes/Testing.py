from abc import ABCMeta, abstractmethod

'''
      {'Type':'Basic Outlier Test',
        'Parameters':[
          {'Name':'Max', 'Data Type':'Float', 'Default Value': 10},
          {'Name':'Min', 'Data Type':'Float'}
        ],
        'Validation Reqs': ['"Max" > "Min"'],
        'Output': 'null'},
      {'Type':'Repeat Value Test', 'Parameters':[
        {'Name': 'Repeating Threshold', 'Data Type': 'Integer'}
      ]},
      {'Type':'Spatial Inconsistency', 'Parameters':[
        {'Name':'Comparision Data', 'Data Type': 'TimeSeries'}, //column name from the same file
        {'Name':'Difference Threshold (%)', 'Data Type': 'Integer'}  //user will be able to select a different column
                                                          //from thier dataset
      ] },
      {'Type': 'Machine Learning', 'Parameters':[
        {'Name': 'Training Set', 'Data Type': 'TimeSeries'}, //column name
        {'Name': 'Percentage Training Data', 'Data Type' : 'Integer'},
        {'Name': 'Percentage Test Data', 'Data Type' : 'Integer'}
      ]}
'''
class Test:

    __metaclass__ = ABCMeta

    def __init__(self, testId = 1, **kwarg):
        self.id = testId
        self.name = "Base Test Class"
    @abstractmethod
    def RunTest(self):
        return False

class RangeTest(Test):
    def __init__ (self, testId = 1, **kwargs):
        self.id = testId
        for parameter in kwargs["Parameters"]:
          if parameter['Name'] == 'Max':
            self.max = parameter['Value']
          elif parameter['Name'] == 'Min':
            self.min = parameter['Value']

    # data must be a float list
    # returns a set of boolean flags 
    def runTest (self, dataframe):
        return []

class SpatialInconsistency(Test):
    def __init__ (self, testId = 1, **kwargs):
        self.id = testId
        for parameter in kwargs["Parameters"]:
          if parameter['Name'] == 'Comparision Data':
            self.comparisonColumn = parameter['Value']
          if parameter['Name'] == 'Difference Threshold (%)':
            self.percentDifference = parameter['Value']

    def RunTest(self, dataframe):
        pass

class RepeatValueTest(Test):
    def __init__ (self, testId = 1, **kwargs):
        self.id = testId
        for parameter in kwargs["Parameters"]:
          if parameter['Name'] == 'Repeating Threshold':
            self.threshold = parameter['Value']
          
    def RunTest(self, dataframe):
        pass