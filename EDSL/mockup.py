from Materia import *

DS = Dataset("data/rockland.csv", numHeaderLines=9)
DS2 = Dataset("data/evergreen.csv")
DS3 = Dataset("data/bigelow_soilMTP_2017.csv", numHeaderLines=2)

DS.genHeadersFromMetadataRows((1,6))

DS.flagcodes().are({"None":"OK", "Repeat Value":"Repeat Value", "Missing Value": "Missing", "Outlier": "Exceeds Range", "Spatial Inconsistency": "Incosistent (Spatial)", "Logical Inconsistency": "Inconsistent (Logical)", "Spike": "Spike"})



series_max = DS['Air temperature (2-meter) monitor_Maximum']
series_min = DS['Air temperature (2-meter) monitor_Minimum']
series_max_10 = DS['Air temperature (10-meter) monitor_Maximum']

series_max.timestep((series_max.beginning(+1)) - series_max.beginning())
series_min.timestep((series_min.beginning(+1)) - series_min.beginning())

def rv_test(value):
    n = 3
    if not value.isnan():
        return value == value.prior(n)

def range_test(value):
    return (value < -7.8 or value > 28)

def spatial_inconsistency(value, i):
    comp_val = series_max_10.value().at(value)
    threshold = abs(value * 2)

    if comp_val > (value + threshold) or comp_val < (value - threshold):
        return True

    return False

def logical_inconsistency_min(min_value):
    max_value = series_max.value().at(min_value)

    if min_value > max_value:
        return True

    return False

def logical_inconsistency(max_value):
    min_val = series_min.value().at(max_value)

    if min_val > max_value:
        return True

    return False

def slope_test(value, i):
    p_a = value.prior(2)[0]
    p_b = value.prior(2)[1]
    p_c = value

    priorslp = 0.0

    if p_a.isScalar() and p_b.isScalar():
        # x values
        x1 = p_a
        x2 = p_b

        # y values
        y1 = p_a.intIndex()
        y2 = p_b.intIndex()

        # current slope
        priorslp = (y2-y1)/(x2-x1)

        # x ad y values for next point
        x3 = p_c
        y3 = p_c.intIndex()

        # next slope
        nextslp = (y3-y2)/(x3-x2)

        if (abs(nextslp) < .1                   #very sharp slope
        and abs(nextslp) < abs(priorslp*.01)    #big difference between the two slopes
        and abs(nextslp) != float("inf")        #slope is not a flat line
        and abs(priorslp) != float("inf")):     #slope is not a flat line
            return True

        return False



series_max.datapoint().flag('Missing Value').missingValueTest(-9999)
series_max.datapoint().flag("Repeat Value").when(rv_test)
series_max.datapoint().flag("Outlier").when(range_test)
series_max.datapoint().flag("Spatial Inconsistency").when(spatial_inconsistency)
series_max.datapoint().flag("Logical Inconsistency").when(logical_inconsistency)
series_max.datapoint().flag("Spike").when(slope_test)

series_min.datapoint().flag('Missing Value').missingValueTest(-9999)
series_min.datapoint().flag("Repeat Value").when(rv_test)
series_min.datapoint().flag("Outlier").when(range_test)
series_min.datapoint().flag("Spatial Inconsistency").when(spatial_inconsistency)
series_min.datapoint().flag("Logical Inconsistency").when(logical_inconsistency_min)
series_min.datapoint().flag("Spike").when(slope_test)



dat = series_max.data()

cnt = 0
for i, flag in enumerate(series_max.flags()):
    if flag.notNone():
        cnt += 1
        # print("Flag: ", flag, "Data: ", dat[i])
print(cnt)

cnt = 0
for i, flag in enumerate(series_min.flags()):
    if flag.notNone():
        cnt += 1

print(cnt)
