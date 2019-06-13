import sys
#sys.path.append("..")
from flask import Flask, jsonify, json, request
from Backend.Classes.Data import DataManager
from Backend.Classes.Statistics import getBasicStatistics
from redis import Redis

app = Flask(__name__)
redis = Redis(host='redis', port=6379)
dataManager = DataManager(redis)

# Service Functionality
@app.route('/')
def index():

	# Try
	try:
		print("Working")
		return("working")

	# Except
	except e:
		print(str(e))
		return False, str(e)


@app.route('/cols/<sessionId>', methods=['GET'])
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
'''
@app.route('/data/<sessionId>', methods=['GET'])
def get_data(sessionId):
	cols = []
	numRows = request.args.get('num_rows')

	if numRows is not None: numRows = int(numRows)
	fileName = dataManager.retrieveFileLoc(sessionId)
	data = dataManager.readAndLoadData(fileName, numRows)

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
		dataColumns = dataManager.retrieveOnlyDataCols(fileName,statColumnList)
		stats = {}
		for columnName in dataColumns:
			stats[columnName] = getBasicStatistics( dataColumns[columnName])
		#data = dataManager.readAndLoadData(fileName)
		#stats = []
		#for col in data:
		#	stats.append(getBasicStatistics(col))
	return jsonify(stats), 200 #jsonify(stats)

# Run Main
if __name__ == '__main__':
	# Set to False when deploying
	app.debug = True
	app.run(host='0.0.0.0', port=8082)
