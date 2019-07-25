#!/usr/bin/env python
import sys
#sys.path.append("..")
from flask import Flask, jsonify, json, request
from Backend.Classes.Data import DataManager
from Backend.Classes.Statistics import getBasicStatistics
from redis import Redis
from flask_cors import cross_origin

app = Flask(__name__)
redis = Redis(host='redis', port=6379)
dataManager = DataManager(redis)

# Service Functionality
@app.route('/')
@cross_origin()
def index():

	obj = {}

	redis.set("test", "3f48")
	obj['debug'] = redis.get("test")

	print(obj)

	return redis.get("test")
	# return jsonify(obj)


@app.route('/cols/<sessionId>', methods=['GET'])
@cross_origin()
def get_columns(sessionId):
    cols = []

    fileName = dataManager.retrieveFileLoc(sessionId)
    data = dataManager.readAndLoadData(fileName, 20)

    for col in data:
        cols.append(col)

    return jsonify(cols)

'''
	Endpoint: get_data
	Example call: /data/fa3cf742-7c1d-11e9-be79-0242ac1b0005?num_rows=20
	Arguments: sessionId - uuid,
				num_rows[optional] - int
	An error occured where redis was unable to retrieve the correct file path from this
	method. Instead it returned none. :/ Restarting redis fixed the problem, but I don't know what happened.
'''
@app.route('/data', methods=['GET'])
@cross_origin()
def get_data():
	cols = []
	data = {}
	numRows = request.args.get('numRows')
	sessionId = request.args.get('sessionId')

	if numRows is not None: numRows = int(numRows)

	filePath = dataManager.retrieveFileLoc(request.args.get('sessionId'))
	data = dataManager.readAndLoadData(filePath, numRows)

	return jsonify(data)

'''
	Endpoint: get_stats
	Description: Returns stats for specified columns in uploaded json
	Requirement: The upload must have a mime type of application/json
	Example call: /stats/fa3cf742-7c1d-11e9-be79-0242ac1b0005
	Arguments: sessionId - uuid, a json file with column names
	Example JSON:
	{'Columns': ['cola','colb','colc']}
	To test with curl: curl -d '{"key1":1}' -X POST
	http://localts/63f7d7dc-8e08-11e9-a87f-0242ac140006
	-H "Content-Type: application/json"
'''
@app.route('/stats/<sessionId>', methods=['Post'])
def get_stats(sessionId):
	print (request.form)
	dataColumns = ''
	statColumnList = ''
	if request.is_json:
		jsonConfig = request.json
		statColumnList = jsonConfig['Columns']

		fileName = dataManager.retrieveFileLoc(sessionId)
		dataColumns = dataManager.retrieveOnlyDataCols(fileName,statColumnList, None)
		stats = {}
		for columnName in dataColumns:
			stats[columnName] = getBasicStatistics( dataColumns[columnName])
		#data = dataManager.readAndLoadData(fileName)
		#stats = []
		#for col in data:
		#	stats.append(getBasicStatistics(col))
	return jsonify(stats), 200 #jsonify(stats)

'''
	Endpont: get_downsampled_data
	Expected Post: {
		dataColList: <list>,
		indexCol: <string>,
		timeStep: <int> (minutes),
		rateOfDownsample: <int> (eg. aggregrate every 3 values)
	}
'''
@app.route('/data/downsampled/<sessionId>', methods=['POST'])
@cross_origin()
def get_downsampled_data(sessionId):
	requestContent = request.json

	filePath = dataManager.retrieveFileLoc(sessionId)
	data = dataManager.retrieveOnlyDataCols(filePath, requestContent['dataColList'], indexName=requestContent['indexCol'])
	data = dataManager.downSample(data, requestContent['timeStep'], requestContent['rateOfDownsample'])

	# store index for later user
	dataManager.setNdxName(sessionId, requestContent['indexCol'])

	return data.to_json()



'''
	Endpont: get_downsampled_data
	Expected Post: {
		dataColList: <list>,
		indexCol: <string>,
		timeStep: <int> (minutes),
		rateOfDownsample: <int> (eg. aggregrate every 3 values)
	}
'''
@app.route('/data/vis/downsampled/<sessionId>', methods=['POST'])
@cross_origin()
def get_downsampled_data_vis(sessionId):
	requestContent = request.json
	formattedData = []
	visData = {}

	filePath = dataManager.retrieveFileLoc(sessionId)
	data = dataManager.retrieveOnlyDataCols(filePath, requestContent['dataColList'], indexName=requestContent['indexCol'])
	data = dataManager.downSample(data, requestContent['timeStep'], requestContent['rateOfDownsample'])

	data = data.fillna("null")

	for col in requestContent['dataColList']:
		for index, row in data.iterrows():
			formattedData.append({
			'x': index,
			'y': row[col]
			})
		visData[col] = formattedData

	with open('/SessionFiles/debug.txt', 'w') as f:
		f.write(json.dumps(visData))

	# store index for later user
	dataManager.setNdxName(sessionId, requestContent['indexCol'])

	return jsonify(visData)

# Run Main
if __name__ == '__main__':
	# Set to False when deploying
	app.debug = True
	app.run(host='0.0.0.0', port=8082)
