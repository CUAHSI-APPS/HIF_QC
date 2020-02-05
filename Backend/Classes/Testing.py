from abc import ABCMeta, abstractmethod
from Backend.Classes.Flagging import Flag
import numpy as np
import pandas as pd
from datetime import timedelta
from Backend.Classes.MachineLearning.ExtremeEventDetection import extreme_event_detection, anomaly_binary_list
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
      ]},
      {'Type': 'Machine Learning', 'Parameters':[
        {'Name': 'Training Set', 'Data Type': 'TimeSeries'}, //column name
        {'Name': 'Percentage Training Data', 'Data Type' : 'Integer'},
        {'Name': 'Percentage Test Data', 'Data Type' : 'Integer'}
      ]}
      {'Type': 'Missing Value Test', 'Parameters':[
        {'Name': 'Missing Value Alias', "Data Type": 'Float'},
        {'Name': 'Time Step', 'Data Type': 'Integer'},
        {'Name': 'Time Step Resolution', 'Data Type': 'Time Resolution', 'Options':['minutes', 'hours', 'days', 'weeks']}
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

class MissingValTest(Test):
        def __init__ (self, testId = 1, **kwargs):
            self.flag = Flag()
            self.id = testId
            self.column = kwargs["Column"]
            self.testName = kwargs["Type"]
            self.isAlias = False

            for parameter in kwargs["Parameters"]:
                if parameter['Name'] == 'Missing Value Alias':
                    if 'Value' in parameter and parameter['Value'] is not '':
                        self.mva = parameter['Value']
                        self.isAlias = True
                        break
                elif parameter['Name'] == 'Time Step':
                    if 'Value' in parameter:
                        self.step = parameter['Value']
                elif parameter['Name'] == 'Time Step Resolution':
                    self.tsr = parameter['Value']

            if self.isAlias is False:
                if self.tsr == 'minutes':
                    self.timeStep = pd.Timedelta(minutes=int(self.step))
                elif self.tsr == 'hours':
                    self.timeStep = pd.Timedelta(hours=int(self.step))
                elif self.tsr == 'days':
                    self.timeStep = pd.Timedelta(days=int(self.step))
                elif self.tsr == 'weeks':
                    self.timeStep = pd.Timedelta(weeks=int(self.step))



        # data must be a float list
        # returns a set of boolean flags
        def runTest (self, dataframe):
            # needs flagging
            if self.isAlias:
                outdf = np.invert(dataframe[self.column] == float(self.mva))
                return outdf.apply(lambda x: self.flag.flag(x, self.testName)), dataframe.index

            dataframe = dataframe.reindex(pd.date_range(start=dataframe.index[0], end=dataframe.index[-1], freq=self.timeStep))
            outdf = dataframe.notna()[self.column]

            return outdf.apply(lambda x: self.flag.flag(x, self.testName)), dataframe.index

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
        dfcopy[self.column] = dfcopy[self.column + '_other'].map(lambda x: not (x >= self.threshold))


        # not x for now. Need to align the true false across datatypes
        return dfcopy[self.column].apply(lambda x: self.flag.flag(x, self.testName))


class ExtremePeakDetection(Test):
  def __init__(self,testId = 1, **kwargs):
        self.flag = Flag()
        self.testName = kwargs["Type"]
        self.id = testId
        self.column = kwargs["Column"]
        self.windowLength = -1
        for parameter in kwargs["Parameters"]:
          if parameter['Name'] == 'Window Length':
            self.windowLength = int(parameter['Value'])
  def runTest(self, dataframe):
    anomalies_output = extreme_event_detection(dataframe[self.column], self.windowLength)
    dfcopy = dataframe.copy()
    dfcopy.name = self.column
    #print(len(anomalies_output[1]))
    #print(len(dfcopy[self.column]))
    dfcopy[self.column] = np.array(anomalies_output[2])
    #print(self.testName)
    #print(dfcopy[self.column].apply(lambda x: self.flag.flag(x, self.testName)))
    return dfcopy[self.column].apply(lambda x: self.flag.flag(x, self.testName))
