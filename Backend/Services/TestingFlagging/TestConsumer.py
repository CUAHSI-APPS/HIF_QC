#!/usr/bin/env python
from kafka import KafkaConsumer
from json import loads
from redis import Redis
from Backend.Classes.Testing import *
from Backend.Classes.Data import *
import math
import time, sys, traceback

class TestConusmer():
    def __init__(self, boostrapServers=['kafka:29092'], groupId='test001'):
        #self.consumer = KafkaConsumer(bootstrap_servers=boostrapServers, group_id = groupId, enable_auto_commit=True, value_deserializer=lambda x: loads(x.decode('utf-8')))
        self.redis = Redis(host='redis', port=6379)
        self.DM = DataManager(self.redis)
        self.flag = Flag()
        self.liveIndex = None

    def combineFlagCols(self, s1, s2):
        goodFlag = self.flag.returnGoodFlag()
        for col, dat in enumerate(s1):
            if s1[col] == '-':
                s1[col] = s2[col]
            elif s1[col] == goodFlag and s2[col] != goodFlag:
                s1[col] = s2[col]
            elif type(s1[col]) is type(0.0) and math.isnan(s1[col]):
                s1[col] = s2[col]
        return s1

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
                sessionId = tests['sessionId']
                timeIndex = tests['timeIndex']

                print(self.redis.get(tests['sessionId']).decode('utf-8'))
                df = pd.read_csv(self.redis.get(tests['sessionId']).decode('utf-8'))
                df[timeIndex] = pd.to_datetime(df[timeIndex])
                df = df.set_index(timeIndex)
                self.liveIndex = df.index

                outdf = pd.DataFrame()

                del (tests['sessionId'])
                del (tests['timeIndex'])

                for col in tests:
                    print(col)
                    for test in tests[col]:
                        test['Column'] = col
                        try:
                            if test['Type'] == 'Basic Outlier Test':
                                print ("Basic Outlier", flush=True)
                                testrunner = RangeTest(1, **test)
                                flags = testrunner.runTest(df)

                            elif test['Type'] == 'Repeat Value Test':
                                print ("Repeat Value Test", flush=True)
                                testrunner = RepeatValueTest(2, **test)
                                flags = testrunner.runTest(df)

                            elif test['Type'] == 'Spatial Inconsistency':
                                print ("Spatial Inconsistency", flush=True)
                                testrunner = SpatialInconsistencyTest(3, **test)
                                flags = testrunner.runTest(df)

                            elif test['Type'] == 'Missing Value Test':
                                # run missingvaltest by default
                                testrunner = MissingValTest(4, **test)
                                flags, self.liveIndex = testrunner.runTest(df)


                            print(len(col), len(flags), flush=True)
                            outdf = outdf.reindex(self.liveIndex)
                            flags = flags.reindex(self.liveIndex)
                            if flags.name+"_flags" not in outdf.columns:
                                # rebase here for alignment if mvt has been run
                                outdf[flags.name+"_flags"] = flags
                            else:
                                # rebase here for alignment if
                                outdf[flags.name+"_flags"] = self.combineFlagCols(outdf[flags.name+"_flags"], flags)


                        except Exception as e:
                            print("there was an error in one of the tests", flush=True)
                            traceback.print_exc(file=sys.stdout)
                            continue





                # set datetime as the index of our flags
                outdf[timeIndex] = self.liveIndex

                outdf = outdf.set_index(timeIndex)


                filename = '/SessionFiles/' + sessionId + '_outputcsv.csv'
                outdf.to_csv(filename)

                self.redis.set(sessionId+'outputcsv', filename)
            # determine what column needs to be ran
            # go to redis based on column number and uid in redis, and test type
            # run test with x test type on column data

consumer = TestConusmer()
print ("START")
consumer.receive()
