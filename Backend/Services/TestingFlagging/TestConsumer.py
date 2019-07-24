#!/usr/bin/env python
from kafka import KafkaConsumer
from json import loads
from redis import Redis
from Backend.Classes.Testing import *
from Backend.Classes.Data import *
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
            if self.redis.llen('jobqueue') > 0:
                print("ONE IN QUEUE", flush=True)
                tests = loads(self.redis.rpop('jobqueue').decode('utf-8'))
                print(self.redis.get(tests['sessionId']).decode('utf-8'))
                df = pd.read_csv(self.redis.get(tests['sessionId']).decode('utf-8'))
                sessionId = tests['sessionId']
                outdf = pd.DataFrame()
                del (tests['sessionId'])
                for col in tests:
                    print(col)
                    for test in tests[col]:
                        test['Column'] = col
                        try:
                            if test['Type'] == 'Basic Outlier Test':
                                testrunner = RangeTest(1, **test)
                                flags = testrunner.runTest(df)
                                # right now this is true and false flags
                                print (flags)
                                print ("Basic Outlier", flush=True)
                                outdf[flags.name + "BOT"] = flags
                            elif test['Type'] == 'Repeat Value Test':
                                print ("RVT", flush=True)
                                testrunner = RepeatValueTest(1, **test)
                                flags = testrunner.runTest(df)
                                #flags.name = flags.name + "RVT"
                                #outdf = outdf.append(flags)
                                outdf[flags.name + "RVT"] = flags
                            elif test['Type'] == 'Spatial Inconsistency':
                                print ("SPATIAL INCONSISTENCY", flush=True)
                                testrunner = SpatialInconsistencyTest(1, **test)
                                flags = testrunner.runTest(df)
                                #flags.name = flags.name + "SI"
                                outdf[flags.name + "SI"] = flags
                        except Exception as e:
                            print ("there was an error in one of the tests", flush=True)
                            continue
                print(outdf.columns, flush=True)
                print(outdf.to_csv(), flush=True)
                self.redis.set(sessionId+'outputcsv', outdf.to_csv())
            # determine what column needs to be ran
            # go to redis based on column number and uid in redis, and test type
            # run test with x test type on column data
            
consumer = TestConusmer()
print ("START")
consumer.receive()