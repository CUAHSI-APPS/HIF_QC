##File: Statistics.py
##Contains: Data Manager Class defintion
## Authors: Chase Carthen, Connor Scully-Allison
## I didn't 'mean' to make this class
import numpy as np

# Mean, Median, SD (limited window), Range, Interquartile Range, Max, Min
def mean(array):
    try:
        return np.mean(array)
    except:
        return 0
def calculateBasicStatistics(array,subset=None):
    maxValue = np.max(array)
    minValue = np.min(array)
    rangeValue = maxValue - minValue
    median = np.median(array)
    mean = np.mean(array)
    q75, q25 = np.percentile(array, [75 ,25])
    iqr = q75 - q25
    