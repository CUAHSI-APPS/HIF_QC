import sys
sys.path.append("..")
sys.path.append("../../classes")
from flask import Flask, jsonify, json, request
from flask_cors import cross_origin
import pyodbc
from Configuration import TestConfiguration

app = Flask(__name__)

# Service Functionality
@app.route('/Config/')
@cross_origin()
def index():

	# Try
	try:
		testconfig = TestConfiguration("../config/tests.config")
		
		print(testconfig.TestParameters)
		
		return("working")

	# Except
	except Exception as e:
		print(str(e))
		return False, str(e)

# Run Main
if __name__ == '__main__':
	# Set to False when deploying
	app.debug = True
	app.run(host='127.0.0.1', port=8081)
