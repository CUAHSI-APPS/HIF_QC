##File: Data.py
##Contains: Data Manager Class defintion
## Authors: Connor Scully-Allison, Chase Carthen

import pandas as pd
from flask import jsonify

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


    def readAndLoadData(self, filePath):
        #variables
        dataDict = {}
        dataJson = ""

        with open(filePath, 'r') as file:
            df = pd.read_csv(file)
            for col in list(df.columns):
                dataDict[col] = list(df[col])

        dataJson = jsonify(dataDict)

        return dataJson
