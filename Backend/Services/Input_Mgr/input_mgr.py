# compose_flask/app.py
from Backend.Classes.TicketCounter import SessionTicketCounter
from Backend.Classes.Data import DataManager
from flask import Flask, jsonify, request, flash
from redis import Redis
from kafka import KafkaProducer
from flask_cors import cross_origin
import email
import json
import pandas as pd
import os

app = Flask(__name__)
redis = Redis(host='redis', port=6379)
SessionTC = SessionTicketCounter()
dataManager = DataManager(redis)


improperFileRequest = "Error no file found."

def get_kafka_prod():
    return KafkaProducer(bootstrap_servers=['kafka:29092'])

@app.route('/')
@cross_origin()
def hello():
    return "Hello world"

@app.route('/testkafka/<msg>')
@cross_origin()
def testkafka(msg):
    prod = get_kafka_prod()
    prod.send('SessionData', value=bytes(msg,encoding="ascii"))
    prod.close()
    return msg

@app.route('/upload/', methods=['POST'])
@cross_origin()
def upload():
    global improperFileRequest

    # check if the post request has the file part
    if 'file' not in request.files:
        #flash('No file part')
        return improperFileRequest, 400

    #http://flask.pocoo.org/docs/1.0/patterns/fileuploads/
    file = request.files['file']
    #print (request)
    # if user does not select file, browser also
    # submit an empty part without filename
    #if file.filename == '':
    #    #flash('No selected file')
    #    return "Error no file found.", 400

    #Change permissions for writing out as sudo or not
    Session = SessionTC.TakeTicket(file.filename)
    filename = '/SessionFiles/' + Session + '.csv'
    with open(filename, 'wb') as F:
        F.write(file.read())

    outputJson = {"status":"Success", "token":Session, "filename": filename}
    redis.set(Session, os.path.abspath(filename))
    return  jsonify(outputJson)


# Delete upon verification of other service working
@app.route('/data/<sessionId>', methods=['GET'])
@cross_origin()
def get_columns(sessionId):
    cols = []

    fileName = dataManager.retrieveFileLoc(sessionId)
    data = dataManager.readAndLoadData(fileName, 20)

    for col in data:
        cols.append(col)

    return jsonify(cols)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
