# compose_flask/app.py
from Backend.Classes.TicketCounter import SessionTicketCounter
from Backend.Classes.Data import DataManager
from flask import Flask, jsonify, request, flash
from redis import Redis
from kafka import KafkaProducer
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
def hello():
    return "Hello world"

@app.route('/testkafka/<msg>')
def testkafka(msg):
    prod = get_kafka_prod()
    prod.send('SessionData', value=bytes(msg,encoding="ascii"))
    prod.close()
    return msg

@app.route('/upload/', methods=['POST'])
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

    #print (file.read())
    #print (file.filename)
    #Change permissions for writing out as sudo or not
    Session = SessionTC.TakeTicket(file.filename)
    filename = '/SessionFiles/' + Session + '.csv'
    with open(filename, 'wb') as F:
        F.write(file.read())

    outputJson = {"status":"Success","token":Session, "filename": filename}
    redis.set(Session, os.path.abspath(filename))
    #jsonify(list(request.form.getlist('test')))
    #jsonify(request.form.get('csvdate') + request.form.get('csvdata'))
    return  jsonify(outputJson)

@app.route('/data/<sessionId>', methods=['GET'])
def get_columns(sessionId):
    print(sessionId)
    fileName = dataManager.retrieveFileLoc(sessionId)

    return dataManager.readAndLoadData(fileName)
    # json = pd.read_csv(filename)

    # return jsonify(list(df1.columns))#str(os.path.exists(redis.get(request.args.get('session_id'))))#jsonify(df1.columns())


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
