import sys
#sys.path.append("..")
from flask import Flask, jsonify, json, request
from Backend.Classes.Data import DataManager
from redis import Redis

app = Flask(__name__)
redis = Redis(host='redis', port=6379)
dataManager = DataManager(redis)

# Service Functionality
@app.route('/')
def index():

	obj = {}

	redis.set("test", "3f48")
	obj['debug'] = redis.get("test")

	print(obj)

	return redis.get("test")
	# return jsonify(obj)


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
	An error occured where redis was unable to retrieve the correct file path from this
	method. Instead it returned none. :/ Restarting redis fixed the problem, but I don't know what happened.
'''
@app.route('/data', methods=['GET'])
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
	Endpont: get_downsampled_data
	Expected Post: {
		dataColList: <list>,
		indexCol: <string>,
		timeStep: <int> (minutes),
		rateOfDownsample: <int> (eg. aggregrate every 3 values)
	}
'''
@app.route('/data/downsampled/<sessionId>', methods=['POST'])
def get_downsampled_data(sessionId):
	requestContent = request.json

	filePath = dataManager.retrieveFileLoc(sessionId)
	data = dataManager.retrieveOnlyDataCols(filePath, requestContent['dataColList'])

	return data.to_json()

# Run Main
if __name__ == '__main__':
	# Set to False when deploying
	app.debug = True
	app.run(host='0.0.0.0', port=8082)
