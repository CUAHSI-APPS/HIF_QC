##File: Data.py
##Contains: Data Manager Class defintion
## Authors: Connor Scully-Allison, Chase Carthen

from flask import jsonify
import json
import pandas as pd
import datetime as dt

'''
Class: Data Manager
Purpose: Manage interaction between redis and file I/O to retrieve data stored
    in csv/xml/etc. files
'''
class DataManager():

    def __init__(self, redis):
        self.redis = redis
        # store important locations
        self.redis.set('session_files', '/SessionFiles/')

    #in case file location becomes more complicated
    def retrieveFileLoc(self, sessionId):
        return self.redis.get(sessionId)

    def setNdxName(self, sessionId, colName):
        self.redis.set(sessionId+"index", colName)

    def getNdxName(self, sessionId):
        self.redis.get(sessionId+"index").decode('utf-8')

    def setTimeColAsNdx(self, sessionId, DataFrame):
        indexCol = self.redis.get(sessionId+"index").decode('utf-8')
        locDF = DataFrame

        # set datetime as the index of our flags
        if indexCol is not None:
            locDF[indexCol] = pd.to_datetime(locDF[indexCol])
            locDF = locDF.set_index(indexCol)

        return locDF

    def getDataAsDf(self, sessionId):
        filePath = self.retrieveFileLoc(sessionId)
        df = None

        with open(filePath, 'r') as file:
            df = pd.read_csv(file)
            df.apply(pd.to_numeric, errors='coerce').fillna(df)

        df = self.setTimeColAsNdx(sessionId, df)

        return df

    def getOutputAsDf(self, sessionId, filePath):
        filePath = filePath
        df = None

        with open(filePath, 'r') as file:
            df = pd.read_csv(file)
            df.apply(pd.to_numeric, errors='coerce').fillna(df)

        df = self.setTimeColAsNdx(sessionId, df)

        return df

    def getCols(self, filePath):
        col = []
        df = None

        with open(filePath, 'r') as file:
            df = pd.read_csv(file)
            df = df.where((pd.notnull(df)), None)

        return list(df.columns)

    # configuration to work with frontend code
    def getData(self, filePath, numRows=None):
        with open(filePath, 'r') as file:
            df = pd.read_csv(file)
            df = df.where((pd.notnull(df)), None)

            if numRows is not None:
                return df.head(n=numRows).values.tolist()
            else:
                return df.values.tolist()


    def readAndLoadData(self, filePath, numRows=None):
        #variables
        dataDict = {}

        with open(filePath, 'r') as file:
            df = pd.read_csv(file)
            df = df.where((pd.notnull(df)), None)

            for col in list(df.columns):
                if numRows is not None:
                    dataDict[col] = list(df[col][:numRows])
                else:
                    dataDict[col] = list(df[col])

        return dataDict

    #After people idntify which cols they want
    def retrieveOnlyDataCols(self, filePath, dataColList, indexName=None):
        # variables
        subframe = None

        with open(filePath, 'r') as file:
            df = pd.read_csv(file)
            df.apply(pd.to_numeric, errors='coerce').fillna(df)

            if indexName is not None:
                # we will have to do some error checking here
                # this function is dangerous af
                df[indexName] = pd.to_datetime(df[indexName])
                df = df.set_index(indexName)

            subframe = df[dataColList]


        return subframe


    def downSample(self, df, timeStep, numberOfBins):

        if timeStep is not None:
            rateOfDownsample = str(timeStep*numberOfBins) + 'T'
            df = df.resample(rateOfDownsample).mean()

        #reformat datetime index
        df.index = df.index.map(lambda x: dt.datetime.strftime(x, '%Y-%m-%dT%H:%M:%SZ'))

        return df

    def storeMetadata(self, sessionId, metaData):
        metaDataLoc = "MD" + sessionId

        #metadata should be a dictonary
        self.redis.set(metaDataLoc, jsonify(metaData))

        return

    def retrieveMetadata(self, sessionId):
        metaDataJson = ""
        metaDataLoc = "MD" + sessionId

        metaDataJson = json.loads(self.redis.get(metaDataLoc))


        return json.loads(metaDataJson)
