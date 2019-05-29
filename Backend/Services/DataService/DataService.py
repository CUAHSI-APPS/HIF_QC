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

# Run Main
if __name__ == '__main__':
	# Set to False when deploying
	app.debug = True
	app.run(host='0.0.0.0', port=8082)
