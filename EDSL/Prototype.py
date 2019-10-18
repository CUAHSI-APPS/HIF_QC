# taking the lead from pandas,
#  internal arrays are numpy representations
import numpy as np
import builtins
import traceback
import sys
from datetime import datetime
from dateutil.parser import parse

from pylms import lms, stage
from pylms.rep import Rep                  # add our snek-lms module




'''
Name: Flag
Description: An object which holds metadata about a flagged datapoint.
Private Members: Flag code, test Parameters/defintion
'''
class Flag():
    pass

'''
Name: TimeSeries
Description: Core data structure. Contains one vector and one TimeSeries.
'''
class TimeSeries():
    def __init__(self, values=None, index=None, timedelta=None, dtype=None):
        # check for valid input index
        self._index = np.array(index, dtype='datetime64')
        self._timedelta = self._guessTimeDelta(_index)

        # check for valid datatypes
        # throw error if datatype does not match value
        self._values = np.array(values, dtype= 'f8' if (dtype is None) else d)

        pass

    '''
    Name: _guessTimeDelta()
    Parameter [array of datetime]: Index
    '''
    def _guessTimeDelta(self, index):
        counts = {};

        if index is None:
            return None

        for i, dt in enumerate(index):
            if(i+1 is not len(index)):
                timedelta = index[i+1] - dt
                if counts[str(timedelta)] is None:
                    counts[str(timedelta)] = 0
                counts[str(timedelta)] += 1

        print(counts)






'''
Name: Dataset
Description: Data-frame like data structure. Comprised of multiple
                time series aligned against particular time-steps.
Planned Funcitonality: Conversion, Write Out, Subselect Columns, Bind Dataset Level Metadata
'''

# a class comprised of multiple time series
# allows for CSV import with different time steps between cols
# may have an intermediary representation
class Dataset():
    def __init__(self, filePath=None, csvString=None, vocab=None, dateTimeFormat=None):
        self._colNames = None
        self._generalMetadata = None
        self._timeCols = None
        self._tCNames = np.empty((0,0), dtype=object)
        self._dataCols = None
        self._addtlCols = None

        if filePath is not None:
            temp = np.genfromtxt(filePath, delimiter=',', dtype=None)

            # we need to put things in proper places
            # unless a vocab is provided lets just assume top row is column names
            self._colNames = temp[0]
            temp = temp[1:-1]

            # convert temp to col major
            # optimization opportunity here I believe
            colmjr = np.empty( (temp.shape[1], temp.shape[0]), dtype=object)

            for i, row in enumerate(temp):
                for j, col in enumerate(self._colNames):
                    colmjr[j][i] = temp[i][j]

            #do a quick search among cols for the word time
            for i, col in enumerate(self._colNames):
                colName = col.upper()
                # put in an arbitrairy number of datetime arrays
                if ((b"TIME" in colName) or (b"DATE" in colName)):
                    if(self._timeCols is None):
                        self._timeCols = np.empty((0, colmjr.shape[1]), dtype='datetime64')

                    self._timeCols = np.vstack([self._timeCols, colmjr[i]]) # not converted to datetimes :(
                    self._tCNames = np.append(self._tCNames, col)

            # convert time cols to datetime
            try:
                self._timeCols = self._timeCols.astype('datetime64')
            except:
                try:
                    print("Gets here")
                    if(dateTimeFormat is not None):
                        for col in self._timeCols:
                            for dt in col:
                                dt = parse(dt)
                    elif(dateTimeFormat is None):
                        for i, col in enumerate(self._timeCols):
                            for j, dt in enumerate(col):
                                self._timeCols[i][j] = parse(dt)

                except:
                    traceback.print_exc(file=sys.stdout)
                    print("\n---------------------------------\n")
                    print("Warning: Dataset unable to automatically translate datetime column to datetime datatpe.")



            print(self._timeCols, self._tCNames)







    pass


'''
Name: Evaluator
Description: Class based around evaluating code written in this language,
                to ensure security of operation. In the future it may also optimize.
'''
class Evaluator():
    pass


'''
The class which contains the library itself.
'''
