import sys
sys.path.append("..")
from flask import Flask, jsonify, json, request
from flask_cors import cross_origin
import pyodbc

app = Flask(__name__)

# Service Functionality
@app.route('/Test/')
@cross_origin()
def index():

	# Try
	try:
		print("Working")
		return("working")

	# Except
	except Exception, e:
		print(str(e))
		return False, str(e)

# Run Main
if __name__ == '__main__':
	# Set to False when deploying
	app.debug = True
	app.run(host='127.0.0.1', port=8085)
