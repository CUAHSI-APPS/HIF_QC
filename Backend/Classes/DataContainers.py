import datetime

"""
"""
class DataBundle:

    def __init__(self, BundleProperty=None, DataStreams=[]):
        self.BundleProperty = BundleProperty
        self.DataStreams = DataStreams

    def SetProperty(self, BundleProperty):
        self.BundleProperty = BundleProperty

    def GetProperty(self):
        return self.BundleProperty

    def SetDataStreams(self, DataStreams):
        self.DataStreams = DataStreams

    def AddDataStream(self, DataStream):
        self.DataStreams.append(DataStream)

    def GetDataStreams(self):
        return self.DataStreams

"""
"""
class DataStream:

    def __init__(self, Measurements=[], MetaData={}):
        self.Measurements = Measurements
        self.StreamID = MetaData["Stream"]
        self.MetaData = MetaData

    def loadMeasurements(self, Measurements):
        self.Measurements = Measurements

    def fetchMeasurements(self):
        return self.Measurements

    def insertMeasurement(self, Measurement):
        self.Measurements.append(Measurement)

    def sortMeasurements(self):
        self.Measurements.sort(key = lambda Measurement: Measurement.TimeStamp)

"""
"""
class Measurement:
    def __init__(self, Value=None, TimeStamp=None, Flag=None, AssociatedStream=None):
        self.Value = Value
        self.TimeStamp = TimeStamp
        self.Flag = Flag
        self.AssociatedStream = AssociatedStream

    def getValue(self):
        return self.Value

    def getTimestamp(self):
        return self.TimeStamp

    def getAssocatedStream(self):
        return self.AssociatedStream

    def setFlag(self, Flag):
        #This function should have a guard for
        # only accepted flag values some range (0-100)
        self.Flag = Flag

    def getFlag(self):
        return self.Flag
