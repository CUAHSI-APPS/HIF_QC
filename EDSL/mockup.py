from Prototype import Dataset

DS = Dataset("data/rockland.csv", numHeaderLines=9)
DS.genHeadersFromMetadataRows((1,6))

DS.flagcodes().are({"Repeat Value":1, "Missing Value": 2, "Outlier": 3})

series1 = DS['Air temperature (2-meter) monitor_Maximum']
series1.timestep((series1.beginning(+1)) - series1.beginning())

def rv_test(value):
    n = 3
    if not value.isnan():
        res = value == value.prior(n)
        if res == True:
            print(res, value, value.prior(n))
        return res

def range_test(value):
    res = (value < -7.8 or value > 28)
    if res == True:
        print(res, value)
    return res

series1.datapoint().flag("Repeat Value").when(rv_test)
series1.datapoint().flag("Outlier").when(range_test)

print(series1.testHistory())

print(series1.flaggedData())
