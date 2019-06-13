##File: Statistics.py
##Contains: Data Manager Class defintion
## Authors: Chase Carthen, Connor Scully-Allison
## I didn't 'mean' to make this class
import numpy as np
from pandas.api.types import is_numeric_dtype

# Mean, Median, SD (limited window), Range, Interquartile Range, Max, Min
def meanArrayValue(array):
    try:
        return np.mean(array)
    except:
        return 0
def minArrayValue(array):
    try:
        return np.min(array)
    except:
        return 0
def maxArrayValue(array):
    try:
        return np.max(array)
    except:
        return 0
def medianArrayValue(array):
    try:
        return np.median(array)
    except:
        return 0
def interquartileQuartileRanges(array):
    try:
        twentyFifthPercentile, SeventyFifthithPercentile = np.percentile(array, [25,75])
        return twentyFifthPercentile, SeventyFifthithPercentile, SeventyFifthithPercentile - twentyFifthPercentile
    except:
        return 0,0,0
# assuming a pandas dataframe for df
def getBasicStatistics(df,subset=None):
    df.replace([None, np.inf, -np.inf], np.nan).dropna(how="all")
    array = list(df)
    if len(array) == 0 or not is_numeric_dtype(df):
        return {"Message":"No statistics for this column."}
    #array = list(filter(np.nan, array))
    maxValue = maxArrayValue(array)
    minValue = minArrayValue(array)
    rangeValue = maxValue - minValue
    medianValue = medianArrayValue(array)
    meanValue = meanArrayValue(array)
    q75, q25, iqr = interquartileQuartileRanges(array)
    return {"Max" : maxValue, "Min" : minValue, "Median": medianValue, "Range": rangeValue, "Mean": meanValue, "Q25" : q25, "Q75": q75, "Interquartile Range": iqr, "Easter Egg": "Easter Egg" }
    