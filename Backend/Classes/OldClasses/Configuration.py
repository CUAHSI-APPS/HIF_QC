from abc import ABCMeta, abstractmethod
import sys
from xml.dom.minidom import parseString


class Configuration:
    __metaclass__ = ABCMeta

    def __init__(self, SourceFile = None):
        self.SourceFile = SourceFile

    @abstractmethod
    def CheckForChanges(self):
        return False

    @abstractmethod
    def Update(self):
        return False




class SourceConfiguration(Configuration):
    #constructor
    def __init__(self, SourceFile=None):
        #variables
        xml = ""
        CachedFilePath = "{}.cached".format(SourceFile)
        self.SourceFile = SourceFile
        self.SourceMetaData = None
        self.XMLString = ""

        #Only try to fetch configuration information
        # if a file source was given
        if SourceFile != None:
            try:
                with open(SourceFile) as CFile:
                    xml = CFile.read()
                    self.SourceMetaData = parseString(xml)
                    self.XMLString = xml

                # Write cached file out for later comparision
                WFile = open(CachedFilePath, 'w+')
                WFile.write(xml)

            except Exception as e:
                print("Unexpected error:", e)
                print("Configuration object failed to fully instantiate.")
                print("If this was a file I/O error please consider changing the path to the configuaration file.")



    def GetSourceInfo(self):
        return self.SourceMetaData

    '''
    Checks for changes in the configuration file by comparing against
    a cached version of the configuration file.
    True = There has been changes
    False = There has been no changes
    '''
    def CheckForChanges(self):
        #replace with a speedy hash comparision function
        with open(self.SourceFile) as AFile:
            with open(self.SourceFile + ".cached") as BFile:
                if AFile.read() != BFile.read():
                    return True
                return False


    def UpdateFilePath(self, SourceFile):
        self.SourceFile = SourceFile



    def Update(self):
        #variables
        xml = ""
        CachedFilePath = "{}.cached".format(self.SourceFile)


        #Only try to fetch configuration information
        # if a file source was given
        if self.SourceFile != None:
                with open(SourceFile) as CFile:
                    xml = CFile.read()
                    self.SourceMetaData = parseString(xml)

                # Write cached file out for later comparision
                WFile = open(CachedFilePath, 'w+')
                WFile.write(xml)

class TestConfiguration(Configuration):

        def __init__(self, SourceFile=None):
            #member variabales
            self.SourceFile = SourceFile
            self.SourceMetaData = None
            self.TestParameters = {}
            self.XMLString = ""

            #variables
            xml = ""
            CachedFilePath = "{}.cached".format(SourceFile)


            #Only try to fetch configuration information
            # if a file source was given
            if SourceFile != None:
                try:
                    with open(SourceFile) as CFile:
                        xml = CFile.read()
                        self.SourceMetaData = parseString(xml)
                        self.XMLString = xml

                    # Write cached file out for later comparision
                    WFile = open(CachedFilePath, 'w+')
                    WFile.write(xml)

                except Exception as e:
                    print("Unexpected error:", e)
                    print("Configuration object failed to fully instantiate.")
                    print("If this was a file I/O error please consider changing the path to the configuaration file.")

                self.TestParameters = self.ExtractTestParams(self.SourceMetaData)


        def GetSourceInfo(self):
            return self.SourceMetaData

        '''
        Checks for changes in the configuration file by comparing against
        a cached version of the configuration file.
        True = There has been changes
        False = There has been no changes
        '''
        def CheckForChanges(self):
            #replace with a speedy hash comparision function
            with open(self.SourceFile) as AFile:
                with open(self.SourceFile + ".cached") as BFile:
                    if AFile.read() != BFile.read():
                        return True
                    return False


        def UpdateFilePath(self, SourceFile):
            self.SourceFile = SourceFile


        def Update(self):
            #variables
            xml = ""
            CachedFilePath = "{}.cached".format(self.SourceFile)


            #Only try to fetch configuration information
            # if a file source was given
            if self.SourceFile != None:
                    with open(SourceFile) as CFile:
                        xml = CFile.read()
                        self.SourceMetaData = parseString(xml)

                    # Write cached file out for later comparision
                    WFile = open(CachedFilePath, 'w+')
                    WFile.write(xml)


        """ Helper Functions """

        """
        Extracts and organizes test Parameters from the XML
        into the configuration object

        Returns: A dictionary which maps a datastream id to
                List of tests
        """
        def ExtractTestParams(self, TestXML):
            #variables
            DataStreams = None
            Tests = None
            TestHolder = {}
            AssociatedTests = []
            TestBundle = {}
            TestBundles = []

            #code
            DataStreams = TestXML.getElementsByTagName("DataStream")

            for Stream in DataStreams:
                StreamID = self.GetInnerXML(Stream.getElementsByTagName("Stream"))
                Tests = Stream.getElementsByTagName("Test")

                #append tests into this test bundle object
                #using a temporary dictionary load data
                #THIS CAN BE PUSHED OUT INTO A FUNCTION
                for Test in Tests:
                    TestHolder["Type"] = self.GetInnerXML(Test.getElementsByTagName("Type"))

                    if TestHolder["Type"] == "Bounds":
                        TestHolder["Max"] = self.GetInnerXML(Test.getElementsByTagName("Max"))
                        TestHolder["Min"] = self.GetInnerXML(Test.getElementsByTagName("Min"))

                    elif TestHolder["Type"] == "Repeat Value":
                        TestHolder["RepeatThreshold"] = self.GetInnerXML(Test.getElementsByTagName("RepeatThreshold"))

                    AssociatedTests.append(TestHolder)

                    TestHolder = {}

                TestBundle[StreamID] = AssociatedTests

                #TestBundles.append(TestBundle)

                #reset our temporary holders
                AssociatedTests = []
                #TestBundle = {}

            return TestBundle


        def GetInnerXML(self, node):
            return node[0].firstChild.nodeValue
