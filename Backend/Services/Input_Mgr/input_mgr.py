# compose_flask/app.py
#from TicketCounter import TicketCounter
from flask import Flask, jsonify, request
from redis import Redis
from kafka import KafkaProducer
import email

app = Flask(__name__)
redis = Redis(host='redis', port=6379)
SessionTC = TicketCounter


def get_kafka_prod():
    return KafkaProducer(bootstrap_servers=['kafka:29092'])

@app.route('/')
def hello():
    redis.incr('hits')
    return 'This Compose/Flask demo has been viewed %s time(s).' % redis.get('hits')

@app.route('/testkafka/<msg>')
def testkafka(msg):
    prod = get_kafka_prod()
    prod.send('SessionData', value=bytes(msg,encoding="ascii"))
    prod.close()
    return msg

@app.route('/upload/', methods=['POST'])
def upload():
    if 'multipart/form-data' in request.headers['Content-Type']:
        input_stream = request.files['file']
        filename = request.files['file'].filename
    else:
        input_stream = request.stream
        filename = "test.csv"

    with open(filename, 'wb') as F:
        F.write(input_stream.read())

    return "Success"

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
