#!/usr/bin/env python
import sys
#sys.path.append("..")
from flask import Flask, jsonify, json, request
from flask_cors import cross_origin
import pandas as pd
from Backend.Classes.Data import DataManager

app = Flask(__name__)
from redis import Redis
from TestProducer import *

redis = Redis(host='redis', port=6379)
testProducer = TestProducer()
dataManager = DataManager(redis)

# Service Functionality
@app.route('/test/')
@cross_origin()
def index():

	# Try
	try:
		print("Working")
		return("working")

	# Except
	except e:
		print(str(e))
		return False, str(e)




@app.route('/test/config/<sessionId>', methods=["POST"])
@cross_origin()
def uploadConfigs(sessionId):
	jsonConfig = None
	configDicts = None

	# check if request is JSON
	if request.is_json:
		jsonConfig = request.json
		jsonConfig['sessionId'] = sessionId
		redis.set(sessionId+"testConfig", json.dumps(jsonConfig))

	# use json for building tests

	# with open('/SessionFiles/debug.txt', 'w') as f:
	# 	f.write(json.dumps(jsonConfig["RS_kw_m2_Min kW/m2 Minimum"]))

	return("Configurations stored successfully.")

@app.route('/test/run/<sessionId>', methods=["GET"])
@cross_origin()
def triggerRunTest(sessionId):
	jsonConfig = redis.get(sessionId+"testConfig")
	testProducer.send(jsonConfig)

	return("Testing Started")


@app.route('/test/result/<sessionId>')
@cross_origin()
def getResult(sessionId):
	fp = redis.get(sessionId+'outputcsv')

	if fp != None:
		fp = fp.decode('utf-8')
		result = dataManager.getOutputAsDf(sessionId, fp)
		indexCol = dataManager.getNdxName(sessionId)

		df = dataManager.getDataAsDf(sessionId)
		df.rename(columns=lambda x: x if x == indexCol else x+"_flags", inplace=True)



		for col in df.columns:
			if col is not indexCol:
				df[col] = df[col].map(lambda x: '-')

		for col in result.columns:
			df[col] = result[col]

		return json.dumps({'csv':df.to_csv()})

	return json.dumps('None')

# Run Main
if __name__ == '__main__':
	# Set to False when deploying
	app.debug = True
	app.run(host='0.0.0.0', port=8085)
