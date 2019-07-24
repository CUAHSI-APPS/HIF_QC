from kafka import KafkaProducer
from json import dumps
from redis import Redis
import time
class TestProducer():
    def __init__(self, boostrapServers=['kafka:29092']):
        self.redis = Redis(host='redis', port=6379)
    def send(self, data):
        time.sleep(1)
        self.redis.rpush('jobqueue', data)
        return self.redis.llen('jobqueue')