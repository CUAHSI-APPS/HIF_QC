from kafka import KafkaProducer
from json import dumps


producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
                         value_serializer=lambda x: 
                         dumps(x).encode('utf-8'))

class TestProducer():
    producer
    def __init__(self, boostrapServers=['kafka:29092']):
        self.producer = KafkaProducer(bootstrap_servers=boostrapServers)
    def send(self, data, topic='test'):
        self.producer.send(topic, value=data)