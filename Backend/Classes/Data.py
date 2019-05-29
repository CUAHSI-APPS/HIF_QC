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

    #After people idntify
    def retrieveOnlyDataCols(self, filePath, dataColList):
        # variables
        dataDict = {}

        with open(filePath, 'r') as file:
            df = pd.read_csv(file)
            df = df.where((pd.notnull(df)), None)
            for col in list(df.columns):
                if col in dataColList:
                    dataDict[col] = list(df[col])

        return dataDict

    def storeMetadata(self, sessionId, metaData):
        metaDataLoc = "MD" + sessionId

        #metadata should be a dictonary
        self.redis.set(metaDataLoc, jsonify(metaData))

        return

    def retrieveMetadata(self, sessionId):
        metaDataJson = ""
        metaDataLoc = "MD" + sessionId

        metaDataJson = self.redis.get(metaDataLoc)


        return json.loads(metaDataJson)
