from Materia import *
import time

DS = Dataset("data/rockland.csv", numHeaderLines=9)
DS2 = Dataset("data/evergreen.csv")
DS3 = Dataset("data/bigelow_soilMTP_2017.csv", numHeaderLines=2)

DS.genHeadersFromMetadataRows((1,6))

DS.flagcodes().are({"None":"OK", "Repeat Value":"Repeat Value", "Missing Value": "Missing", "Outlier": "Exceeds Range", "Spatial Inconsistency": "Incosistent (Spatial)", "Logical Inconsistency": "Inconsistent (Logical)", "Spike": "Spike", "Hardware Range": "Exceeds Hardware Range"})

series_max = DS['Air temperature (2-meter) monitor_Maximum']
series_min = DS['Air temperature (2-meter) monitor_Minimum']
series_max_10 = DS['Air temperature (10-meter) monitor_Maximum']
series_avg_2 = DS['Air temperature (2-meter) monitor_Average']
series_avg_10 = DS['Air temperature (10-meter) monitor_Average']

series_max.timestep((series_max.beginning(+1)) - series_max.beginning())
series_min.timestep((series_min.beginning(+1)) - series_min.beginning())
series_avg_2.timestep((series_min.beginning(+1)) - series_min.beginning())

def rv_test(value):
    n = 3
    if not value.isnan():
        return value == value.prior(n)

def range_test(value):
    return (value < -20 or value > 20)

def hardware_range_test(value):
    return (value < -100 or value > 100)

def spatial_inconsistency(value, i):
    comp_val = series_max_10.value().at(value)
    threshold = abs(value * 2)

    if comp_val > (value + threshold) or comp_val < (value - threshold):
        return True

    return False

def avg_spatial_inconsistency(value, i):
    comp_val = series_avg_10.value().at(value)
    diff = value - comp_val
    avg = (value + comp_val) / 2
    threshold = 2

    threshold = abs(diff / avg) * 100.0 < threshold

    if comp_val > (value + threshold) or comp_val < (value - threshold):
        return True

    return False

def logical_inconsistency_min(min_value):
    max_value = series_max.value().at(min_value)

    if min_value > max_value:
        return True

    return False

# checks for logical inconsistency in DataSet
# eg. max value is less than min value
def logical_inconsistency(max_value):
    min_val = series_min.value().at(max_value)

    if min_val > max_value:
        return True

    return False

# compares slopes between values
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

for i in range(10):

    timedeltas = []

    print("\n Missing Value Test ---------------------")
    start = time.time()
    series_avg_2.datapoint().flag('Missing Value').missingValueTest(-9999)
    end = time.time()

    print(end-start)

    timedeltas.append(end-start)

    print("\n Repeat Value Test ---------------------")
    start = time.time()
    series_avg_2.datapoint().flag("Repeat Value").when(rv_test)
    end = time.time()

    print(end-start)

    timedeltas.append(end-start)

    print("\n Outlier Inconsistency ---------------------")
    start = time.time()
    series_avg_2.datapoint().flag("Outlier").when(range_test)
    end = time.time()

    print(end-start)

    timedeltas.append(end-start)

    print("\n Spatial Inconsistency ---------------------")
    start = time.time()
    series_avg_2.datapoint().flag("Spatial Inconsistency").when(avg_spatial_inconsistency)
    end = time.time()

    print(end-start)

    timedeltas.append(end-start)

    print("\n Logical Inconsistency ---------------------")
    start = time.time()
    series_max.datapoint().flag("Logical Inconsistency").when(logical_inconsistency)
    end = time.time()

    print(end-start)

    timedeltas.append(end-start)

    print("\n Spike Test ---------------------")
    start = time.time()
    series_avg_2.datapoint().flag("Spike").when(slope_test)
    end = time.time()

    print(end-start)

    timedeltas.append(end-start)

    with open('experiments_edsl.csv', 'a') as f:
        f.write('\n')
        for i, d in enumerate(timedeltas):
            if i is len(timedeltas)-1:
                f.write(str(d))
            else:
                f.write(str(d)+', ')
