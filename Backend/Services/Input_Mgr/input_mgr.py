# compose_flask/app.py
from Backend.Classes.TicketCounter import SessionTicketCounter
from flask import Flask, jsonify, request
from redis import Redis
from kafka import KafkaProducer
import email

app = Flask(__name__)
redis = Redis(host='redis', port=6379)
SessionTC = SessionTicketCounter()


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
    Session = SessionTC.TakeTicket()

    if 'multipart/form-data' in request.headers['Content-Type']:
        input_stream = request.files['file']
    else:
        input_stream = request.stream

    filename = Session + '.csv'

    with open(filename, 'wb') as F:
        F.write(input_stream.read())

    return "Success"

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
