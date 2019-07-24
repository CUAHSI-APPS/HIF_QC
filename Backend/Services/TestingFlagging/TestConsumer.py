#!/usr/bin/env python
from kafka import KafkaConsumer
from json import dumps
from redis import Redis
from Backend.Classes.Testing import *
import time
class TestConusmer():
    def __init__(self, boostrapServers=['kafka:29092'], groupId='test001'):
        #self.consumer = KafkaConsumer(bootstrap_servers=boostrapServers, group_id = groupId, enable_auto_commit=True, value_deserializer=lambda x: loads(x.decode('utf-8')))
        self.redis = Redis(host='redis', port=6379)
    def receive(self):
        run = True
        while (run):
            #print ("HERE NOW YALL")
            #time.sleep(10)
            #print ("mark")
            #print (self.redis.llen('jobqueue'))
            #if self.redis.llen('jobqueue') > 0:
            if self.redis.lindex('jobqueue', 0) == None:
                pass
            else:
                print('comeone', flush=True)
                print(self.redis.lindex('jobqueue', 0),flush=True)
                print (self.redis.lpop('jobqueue').decode('utf-8'), flush=True)
            #return
            #print ("now we do something with the message: %s", msg)
            #tests = dumps(msg.decode("utf-8"))
            #print (msg)
            '''for col in tests:
                print(col)
                for test in tests[col]:
                    if test['Type'] == 'Basic Outlier Test':
                        #test['column'] = col
                        #RangeTest(1, **test)
                        print ("Basic Outlier")
                    elif test['Type'] == 'Repeat Value Test':
                        print ("RVT")
                    elif test['Type'] == 'Spatial Inconsistency':
                        print ("SPATIAL INCONSISTENCY")
            '''
            # determine what column needs to be ran
            # go to redis based on column number and uid in redis, and test type
            # run test with x test type on column data
consumer = TestConusmer()
print ("START")
consumer.receive()