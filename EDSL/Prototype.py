# taking the lead from pandas,
#  internal arrays are numpy representations
import numpy as np
import builtins
import traceback
import sys
from datetime import datetime
from dateutil.parser import parse





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
    def __init__(self, filePath=None, csvString=None, numHeaderLines=1, dateTimeFormat=None ):
        self._colNames = None
        self._headerMetadata = None
        self._timeCols = None
        self._tCNames = np.empty((0,0), dtype=object)
        self._floatCols = None
        self._intCols = None
        self._addtlCols = None
        self._ndxMap = {'int':[], 'float':[], 'datetime':[], 'string':[]}     #array of tuples mapping global indexes to local indexes


        if filePath is not None:
            nptemp = None

            try:
                nptemp = np.genfromtxt(filePath, delimiter=',', dtype=None, encoding=None)
            except:
                with open(filePath, 'r') as f:
                    line = f.readline()
                    numvals = len(line.split(","))

                    temp = []
                    temp.append(list(map(lambda x: None if x is '' else x, line.replace('\n','').split(","))))
                    while line:
                        line = f.readline()
                        n = len(line.split(","))
                        if n is numvals:
                            temp.append(list(map(lambda x: None if x is '' else x, line.replace('\n','').split(","))))
                        else:
                            line_arr = list(map(lambda x: None if x is '' else x, line.replace('\n','').split(",")))
                            for i in range(n, numvals):
                                line_arr.append(None)
                            temp.append(line_arr)

                    nptemp = np.array(temp)




            # load all header columns into _headerMetadata
            self._headerMetadata = nptemp[0:numHeaderLines]
            nptemp = nptemp[numHeaderLines:-1]


            #
            # # convert temp to col major
            # # optimization opportunity here I
            colmjr = np.empty( (nptemp.shape[1], nptemp.shape[0]), dtype=object)

            for i, row in enumerate(nptemp):
                for j in range(0,nptemp.shape[1]):
                    colmjr[j][i] = nptemp[i][j]

            self.detectDatatypes(colmjr)





    def detectDatatypes(self, colmjr):
        localindexes = {"dt":0, "int":0, "other":0, "float":0}
        self._floatCols = np.empty((0, colmjr.shape[1]), dtype='float')
        self._intCols = np.empty((0, colmjr.shape[1]), dtype='int')
        self._timeCols = np.empty((0, colmjr.shape[1]), dtype='datetime64')
        self._addtlCols = np.empty((0, colmjr.shape[1]), dtype='object')
        # detect datatypes
        for i, col in enumerate(colmjr):
            try:
                col = col.astype(float)
                self._floatCols = np.vstack([self._floatCols, col])
                self._ndxMap["float"].append((i, localindexes['float']))
                localindexes['float'] += 1
            except:
                try:
                    col = col.astype(int)
                    self._intCols = np.vstack([self._intCols, col])
                    self._ndxMap["int"].append((i, localindexes['int']))
                    localindexes['int'] += 1
                except:
                    try:
                        col = col.astype('datetime64')
                        self._timeCols = np.vstack([self._timeCols, col])
                        self._ndxMap["datetime"].append((i, localindexes['dt']))
                        localindexes['dt'] += 1
                    except:
                        try:
                            if(dateTimeFormat is not None):
                                for dt in col:
                                    dt = parse(dt)
                            elif(dateTimeFormat is None):
                                for j, dt in enumerate(col):
                                    col[j] = parse(dt)

                            self._timeCols = np.vstack([self._timeCols, col])
                            self._ndxMap["datetime"].append((i, localindexes['dt']))
                            localindexes['dt'] += 1
                        except:
                            self._addtlCols = np.vstack([self._addtlCols, col])
                            self._ndxMap['string'].append((i, localindexes['other']))
                            localindexes['other'] += 1

        print(self._addtlCols.dtype)
        print(self._timeCols.dtype)
        print(self._floatCols.dtype)
        print(self._ndxMap)

    def configureDateTime(self):
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

    # overloaded print class goes here



'''
The class which contains the library itself.
'''
