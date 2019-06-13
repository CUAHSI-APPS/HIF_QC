##File: Data.py
##Contains: Data Manager Class defintion
## Authors: Connor Scully-Allison, Chase Carthen

from flask import jsonify
import json
import pandas as pd

'''
Class: Data Manager
Purpose: Manage interaction between redis and file I/O to retrieve data stored
    in csv/xml/etc. files
'''
class DataManager():

    def __init__(self, redis):
        self.redis = redis

    #in case file location becomes more complicated
    def retrieveFileLoc(self, sessionId):
        return self.redis.get(sessionId)

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
    def retrieveOnlyDataCols(self, filePath, dataColList, indexName):
        # variables
        subframe = None

        with open(filePath, 'r') as file:
            df = pd.read_csv(file)
            df = df.where((pd.notnull(df)), None)
            subframe = df[dataColList]

        return subframe

    def downSample(self, df, timeSeriesCol, timeStep, numberOfBins):
        rateOfDownsample = '' + timeStep + numberOfBins
        df = df.resample(rateOfDownsample, on=timeSeriesCol).mean()

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
