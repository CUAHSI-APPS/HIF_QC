from abc import ABCMeta, abstractmethod
from Backend.Classes.Flagging import Flag
import numpy as np

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

def flagTests(value, standard="", test=""):
  if value:
    return "True"
  else:
    return "False"

class Test:

    __metaclass__ = ABCMeta

    def __init__(self, testId = 1, **kwargs):
        self.id = testId
        self.name = "Base Test Class"
        self.column = kwargs["Column"]
        self.flag = Flag()
    @abstractmethod
    def runTest(self):
        return False

class RangeTest(Test):
    def __init__ (self, testId = 1, **kwargs):
        self.flag = Flag()
        self.id = testId
        self.column = kwargs["Column"]
        self.testName = kwargs["Type"]
        self.max = 100
        self.min = 10

        for parameter in kwargs["Parameters"]:
          if parameter['Name'] == 'Max':
            self.max = float(parameter['Value'])
          elif parameter['Name'] == 'Min':
            self.min = float(parameter['Value'])

    # data must be a float list
    # returns a set of boolean flags
    def runTest (self, dataframe):
        # needs flagging
        outdf = np.logical_and(dataframe[self.column] < self.max, dataframe[self.column] > self.min)
        return outdf.apply(lambda x: self.flag.flag(x, self.testName))

class SpatialInconsistencyTest(Test):
    def __init__ (self, testId = 1, **kwargs):
        self.flag = Flag()
        self.testName = kwargs["Type"]
        self.id = testId
        self.column = kwargs["Column"]

        for parameter in kwargs["Parameters"]:
          if parameter['Name'] == 'Comparision Data':
            self.comparisonColumn = parameter['Value']
          if parameter['Name'] == 'Difference Threshold (%)':
            self.percentDifference = float(parameter['Value'])

    def runTest(self, dataframe):
        outdf = np.abs(dataframe[self.column] - dataframe[self.comparisonColumn]) / ((dataframe[self.column]+dataframe[self.comparisonColumn]/2.0)) * 100.0 < self.percentDifference
        outdf.name = self.column

        return outdf.apply(lambda x: self.flag.flag(x, self.testName))

class RepeatValueTest(Test):
    def __init__ (self, testId = 1, **kwargs):
        self.flag = Flag()
        self.id = testId
        self.column = kwargs["Column"]
        self.testName = kwargs["Type"]
        self.threshold = 1

        for parameter in kwargs["Parameters"]:
          if parameter['Name'] == 'Repeating Threshold':
            self.threshold = int(parameter['Value'])

    def runTest(self, dataframe):
        dfcopy = dataframe.copy()

        # get repeating or unique ids for repeating values
        dfcopy['cumsum'] = (dfcopy[self.column] != dfcopy[self.column].shift(1)).cumsum()

        # group all values by count of cumsum "id"
        # and filter down to only incidents of repeat value
        counts = dfcopy[['cumsum',self.column]].groupby(['cumsum']).agg('count')
        counts_less = counts.loc[counts[self.column] > 1]

        # join the multiple counts back to the main df
        dfcopy = dfcopy.join(counts_less, on='cumsum', lsuffix='_caller', rsuffix='_other')

        # load our original values with booleans expressing if they exceed the threshold or not
        dfcopy[self.column] = dfcopy[self.column + '_other'].map(lambda x: x >= self.threshold)

        # Didn't quite work properly. the above algorithm does work however
        #
        # dfcopy['cumsum'] = (dfcopy[self.column] != dfcopy[self.column].shift(1)).cumsum()
        # groups = dfcopy.groupby('cumsum', as_index=False).apply(lambda x: (x.shape[0], x[self.column].index[0]))
        # dfcopy[self.column ] = False
        # for group in groups:
        #   start = group[1]
        #   count = group[0]
        #   dfcopy[self.column ][start:start+count] = count == self.threshold   # hopefully it works :). Test this line of code.
        #
        # dfcopy[self.column ] = dfcopy[self.column ].astype(bool,False)

        print(dfcopy[self.column].apply(lambda x: self.flag.flag((not x), self.testName)))

        # not x for now. Need to align the true false across datatypes
        return dfcopy[self.column].apply(lambda x: self.flag.flag((not x), self.testName))
