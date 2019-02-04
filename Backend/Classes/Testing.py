from abc import ABCMeta, abstractmethod
from datetime import datetime, timedelta
from DataContainers import Measurement
import re

#Global Constants
REPEAT_VALUE_FLAG = 1
OUT_OF_BOUNDS_FLAG = 2
MISSING_VALUE_FLAG = 3
ALL_GOOD_FLAG = 4




class Tester:

    def __init__(self, TestParameters = None, DataStream = None):
        self.DataStream = DataStream
        self.TestParameters = TestParameters
        self.Tests = []
        self.TestedDataPoints = []

        self.Tests = self.ConstructTests(TestParameters)



    def RunTests(self):
        #variabales
        PossibleRepeatValues = []
        MissingValueTuple = []
        NewlySpawnedMeasurements = []

        #Sort By Timestamp to Ensure Everything is sequential

        for Ndx, Measurement in enumerate(self.DataStream.Measurements):

            # Guard against checking against null values
            if(Measurement.Value != None):

                for Test in self.Tests:

                    if Test.id == "MVT":
                        if Ndx >= 2:
                            MissingValueTuple = self.DataStream.Measurements[Ndx-1: Ndx]
                            MissingValueTuple.append(Measurement)
                            NewlySpawnedMeasurements.extend( Test.RunTest(MissingValueTuple, self.DataStream.StreamID) )



                    #Out of bounds test (flag number is 2)
                    elif Test.id == "OBT":
                        Measurement = Test.RunTest(Measurement)
                        if Measurement.Flag == OUT_OF_BOUNDS_FLAG:
                            self.TestedDataPoints.append(Measurement)
                            break

                    #Repeat value test (flag value is 1)
                    elif Test.id == "RVT":
                        NumDataPoints = Test.GetTestRequiredDataPoints()
                        if Ndx >= NumDataPoints:
                            PossibleRepeatValues = self.DataStream.Measurements[ Ndx-NumDataPoints : Ndx ]
                            PossibleRepeatValues.append( Measurement )
                            Measurement = Test.RunTest( PossibleRepeatValues )

                            if Measurement.Flag == REPEAT_VALUE_FLAG:
                                self.TestedDataPoints.append(Measurement)
                                break

                #All tests passed (Flag Data as good)
                if Measurement.Flag == None:
                    Measurement.setFlag(ALL_GOOD_FLAG)
                    self.TestedDataPoints.append(Measurement)

        self.TestedDataPoints.extend(NewlySpawnedMeasurements)

        self.DataStream.Measurements = self.TestedDataPoints

        for Measurement in self.DataStream.Measurements:
            if type(Measurement.TimeStamp) != "str":
                Measurement.TimeStamp = str(Measurement.TimeStamp)

        self.DataStream.sortMeasurements()

    def ConstructTests(self, TestParams):
        #variabales
        Tests = []

        Tests.append( MissingValueTest() )

        for TestInfo in TestParams:
            if TestInfo["Type"] == "Bounds":
                Tests.append( OutOfBoundsTest( "OBT" , TestInfo["Max"], TestInfo["Min"] ) )
            elif TestInfo["Type"] == "Repeat Value":
                Tests.append( RepeatValueTest( "RVT" , TestInfo["RepeatThreshold"] ) )

        return Tests


class Test:

    __metaclass__ = ABCMeta

    def __init__(self, TestID = ""):
        self.id = TestID

    @abstractmethod
    def RunTest():
        return False



class MissingValueTest(Test):
    def __init__(self, TestID = "MVT"):
        self.id = TestID

    def RunTest(self, MeasurementPair, StreamID):

        #variables
        First = MeasurementPair[0]
        Second = MeasurementPair[1]
        Delta = None
        TimeStampOffset = None
        NewMeasurements = []
        #Compare zeorth measurement timestamp against 1st
        # If they are greater than 10mins apart create measuremt,
        # Flag and eject
        p = re.compile(r'\b(\w+[.]\w+)')

        if(type(First.TimeStamp) != "str" or type(Second.TimeStamp) != "str"):
            First.TimeStamp = str(First.TimeStamp)
            Second.TimeStamp = str(Second.TimeStamp)

        Check2 = p.search(Second.TimeStamp[:-1])

        Check1 = p.search(First.TimeStamp[:-1])


        if Check2 is None:
            TimeStamp2 = datetime.strptime(Second.TimeStamp[:-1], '%Y-%m-%d %H:%M:%S')
        else:
            Check2.group()
            TimeStamp2 = datetime.strptime(Second.TimeStamp[:-1], '%Y-%m-%d %H:%M:%S.%f')

        if Check1 is None:
            TimeStamp1 = datetime.strptime(First.TimeStamp[:-1], '%Y-%m-%d %H:%M:%S')
        else:
            Check1.group()
            TimeStamp1 = datetime.strptime(First.TimeStamp[:-1], '%Y-%m-%d %H:%M:%S.%f')

        #TimeStamp2 = datetime.strptime(Second.TimeStamp[:-1], '%Y-%m-%d %H:%M:%S')
        #TimeStamp1 = datetime.strptime(First.TimeStamp[:-1], '%Y-%m-%d %H:%M:%S')
        Delta = TimeStamp2 - TimeStamp1

        if (Delta.seconds / 60) > 10:

            for ndx in range( int(Delta.seconds/60/10) ):

                TimeStampOffset = timedelta(0, ndx*60*10)

                if TimeStamp1 + TimeStampOffset != TimeStamp1:
                    NewMeasurements.append( Measurement( None, str(TimeStamp1 + TimeStampOffset) , MISSING_VALUE_FLAG, StreamID ) )

            return NewMeasurements

        return []




class OutOfBoundsTest(Test):
    def __init__(self, TestID = "OBT", UpperBound = 0, LowerBound = 0):
        self.id = TestID
        self.Max = float(UpperBound)
        self.Min = float(LowerBound)

    def RunTest(self, Measurement):
        if Measurement.Value > self.Max:
            Measurement.setFlag(2)
            return Measurement

        elif Measurement.Value < self.Min:
            Measurement.setFlag(2)
            return Measurement

        else:
            return Measurement


class RepeatValueTest(Test):
    def __init__(self, TestID = "RVT", NumDataPoints=0):
        self.id = TestID
        self.NumDataPoints = int(NumDataPoints)

    #returns the number of datapoints required to
    #run the repeat value test includes the
    #datapoint to be measured
    def GetTestRequiredDataPoints(self):
        return self.NumDataPoints - 1

    def RunTest(self, MeasurementsList):

        if len(MeasurementsList) != self.NumDataPoints:
            raise ValueError

        TestedMeasurement = MeasurementsList[ self.NumDataPoints-1 ]
        MeasurementsList = MeasurementsList[:-1]

        #test the first element against all subsequent elements
        #if equivalent keep going elsewise kick out as unflagged
        for Measurement in MeasurementsList:
            if TestedMeasurement.Value != Measurement.Value:
                return TestedMeasurement

        TestedMeasurement.setFlag(1)
        return TestedMeasurement
