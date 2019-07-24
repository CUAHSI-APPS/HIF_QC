#!/usr/bin/env python
import sys
#sys.path.append("..")
from flask import Flask, jsonify, json, request
from flask_cors import cross_origin

app = Flask(__name__)
from redis import Redis
from TestProducer import *

redis = Redis(host='redis', port=6379)
testProducer = TestProducer()
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
		testProducer.send(json.dumps(jsonConfig))

	# use json for building tests
	
	# with open('/SessionFiles/debug.txt', 'w') as f:
	# 	f.write(json.dumps(jsonConfig["RS_kw_m2_Min kW/m2 Minimum"]))

	return(jsonConfig)

@app.route('/test/result/<sessionId>')
@cross_origin()
def getResult(sessionId):
	result = redis.get(sessionId+'outputcsv')
	if result != None:
		return result
	return 'None'

# Run Main
if __name__ == '__main__':
	# Set to False when deploying
	app.debug = True
	app.run(host='0.0.0.0', port=8085)
