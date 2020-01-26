from Testing import RepeatValueTest, RangeTest, SpatialInconsistencyTest, LogicalInconsistencyTest, MissingTimestampsTest, SpikeTest
import pandas as pd
import time


# {'Type':'Basic Outlier Test',
#   'Parameters':[
#     {'Name':'Max', 'Data Type':'Float', 'Default Value': 10},
#     {'Name':'Min', 'Data Type':'Float'}
#   ],
#   'Validation Reqs': ['"Max" > "Min"'],
#   'Output': 'null'},
# {'Type':'Repeat Value Test', 'Parameters':[
#   {'Name': 'Repeating Threshold', 'Data Type': 'Integer'}
# ]},
# {'Type':'Spatial Inconsistency', 'Parameters':[
#   {'Name':'Comparision Data', 'Data Type': 'TimeSeries'}, //column name from the same file
#   {'Name':'Difference Threshold (%)', 'Data Type': 'Integer'}  //user will be able to select a different column
#                                                     //from thier dataset
# ] }

df = pd.read_csv('rockland.csv')


df['Time Stamp ((UTC-08:00) Pacific Time (US & Canada))'] = pd.to_datetime(df['Time Stamp ((UTC-08:00) Pacific Time (US & Canada))'])


for i in range(0,3):

    timedeltas = []


    testspec = {}

    testspec['Type'] = 'Spike Test'
    testspec['Parameters'] = []
    testspec['Parameters'].append({'Name':'Slope Change Threshold', 'Data Type': 'Float', 'Value': 1 })
    testspec['Column'] = 'TC_C_2_Avg degC Average'


    st = SpikeTest(2, **testspec)


    print("\n Spike Test ---------------------")
    start = time.time()
    st.runTest(df)
    end = time.time()

    print(end-start)

    timedeltas.append(end-start)


    testspec = {}

    testspec['Type'] = 'Basic Outlier Test'
    testspec['Parameters'] = []
    testspec['Parameters'].append({'Name':'Max', 'Data Type': 'Float', 'Value': 20})
    testspec['Parameters'].append({'Name':'Min', 'Data Type': 'Float', 'Value': -20})
    testspec['Column'] = 'TC_C_2_Avg degC Average'

    rt = RangeTest(1, **testspec)


    print("\n Basic Outlier Test ---------------------")

    start = time.time()
    rt.runTest(df)
    end = time.time()

    print(end-start)
    timedeltas.append(end-start)

    testspec = {}

    testspec['Type'] = 'Spatial Inconsistency'
    testspec['Parameters'] = []
    testspec['Parameters'].append({'Name':'Comparision Data', 'Data Type': 'TimeSeries', 'Value': 'TC_C_10_Avg degC Average' })
    testspec['Parameters'].append({'Name':'Difference Threshold (%)', 'Data Type': 'Integer', 'Value': 2})
    testspec['Column'] = 'TC_C_2_Avg degC Average'

    start = time.time()
    sit = SpatialInconsistencyTest(2, **testspec)
    end = time.time()

    print("\n Spatial Inconsistency Test ---------------------")

    start = time.time()
    sit.runTest(df)
    end = time.time()

    print(end-start)
    timedeltas.append(end-start)


    testspec = {}

    testspec['Type'] = 'Logical Inconsistency'
    testspec['Parameters'] = []
    testspec['Parameters'].append({'Name':'Comparision Data', 'Data Type': 'TimeSeries', 'Value': 'TC_C_2_Min degC Minimum' })
    testspec['Parameters'].append({'Name':'Test', 'Data Type': 'String', 'Value': 'Max > Min'})
    testspec['Column'] = 'TC_C_2_Max degC Maximum'


    lit = LogicalInconsistencyTest(2, **testspec)


    print("\n Logical Inconsistency Test ---------------------")
    start = time.time()
    lit.runTest(df)
    end = time.time()

    print(end-start)
    timedeltas.append(end-start)

    testspec = {}

    testspec['Type'] = 'Repeat Value Test'
    testspec['Parameters'] = []
    testspec['Parameters'].append({'Name':'Repeating Threshold', 'Data Type': 'Interger', 'Value': 3 })
    testspec['Column'] = 'TC_C_2_Avg degC Average'


    rvt = RepeatValueTest(2, **testspec)


    print("\n Repeat Value Test ---------------------")
    start = time.time()
    rvt.runTest(df)
    end = time.time()

    print(end-start)
    timedeltas.append(end-start)


    testspec = {}

    testspec['Type'] = 'Missing Timestamps'
    testspec['Parameters'] = []
    testspec['Parameters'].append({'Name':'Time Step', 'Data Type': 'Integer', 'Value': 1 })
    testspec['Parameters'].append({'Name':'Precision', 'Data Type': 'String', 'Value': 'm'})
    testspec['Column'] = 'Time Stamp ((UTC-08:00) Pacific Time (US & Canada))'


    mtt = MissingTimestampsTest(2, **testspec)


    print("\n Missing Timestamps Test ---------------------")
    start = time.time()
    mtt.runTest(df)
    end = time.time()

    print(end-start)
    timedeltas.append(end-start)

    with open('experiments.csv', 'a') as f:
        f.write('\n')
        for i, d in enumerate(timedeltas):
            if i is len(timedeltas)-1:
                f.write(str(d))
            else:
                f.write(str(d)+', ')
