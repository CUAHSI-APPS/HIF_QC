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
        self._timedelta = None

        # check for valid datatypes
        # throw error if datatype does not match value
        self._values = np.array(values, dtype= 'f8' if (dtype is None) else dtype)


    """
---- Fluent Syntax Methods ----------------------
    """
    def datapoint(self):
        return self

    def flag(self, arg):
        print(arg)
        return self

    def when(self, funct):
        print(funct)
        return self

    def timestep(self, timestep):
        print(timestep)
        return self

    """
---- Sugar Functions ------------------------
    """
    def beginning(self):
        return 0

    def end(self):
        return len(self._index)-1




    """
---- Private Functions -----------------------
    """







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
        # public
        self.seriesHeaders = []

        # Private
        self._headerMetadata = []
        self._timeCols = None
        self._floatCols = None
        self._intCols = None
        self._addtlCols = None
        self._ndxMap = []   #array of tuples mapping global indexes to local indexes
        self._flagCols = None

        self._index = None #index itself
        self._indexCol = None #col number

        #fluent interface functionality
        self._state = {}
        self._callChain = []


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

            try:
                if len(self._headerMetadata) is 1:
                    self._seriesHeaders = np.array(self._headerMetadata[0])
                elif len(self._headerMetadata) is 0:
                    raise Exception('Warning: No header columns detected, please assign column names manually.')
                else:
                    defaults = []
                    for i in range(0, nptemp.shape[1]):
                        defaults.append('Series_'+str(i))
                    self._seriesHeaders = np.array(defaults)
            except Exception:
                print('\n--------------------------------')
                print(Exception.args()[0])


            #
            # # convert temp to col major
            # # optimization opportunity here I
            colmjr = np.empty( (nptemp.shape[1], nptemp.shape[0]), dtype=object)

            for i, row in enumerate(nptemp):
                for j in range(0,nptemp.shape[1]):
                    colmjr[j][i] = nptemp[i][j]

            self._detectDatatypes(colmjr)

            if len(self._timeCols) > 0:
                for i, ndx in enumerate(self._ndxMap):
                    if ndx[0] is 'datetime':
                        self._index = self._timeCols[ndx[1]]
                        self._indexCol = i #mapped by default to time series
            else:
                self._index = None


    '''
----- Fluent Syntax Methods --------------------
    '''

    def flags(self):
        return self

    def are(self, flag_configs):
        print("")
        return self

    '''
------ Overloaded Operators -------------------
    '''
    def __repr__(self):
        return '<Dataset>'

    def __str__(self):
        template  = ''
        with open('output_templates/DatasetStrTemplate.txt', 'r') as f:
            template = f.read()

        mdlines = np.array2string(self._headerMetadata)


        headerlines = self._seriesHeaders

        # assemble top
        top = []
        for i in range(0, 4):
            line = []
            if self._index is not None:
                line.append(self._index[i])
            else:
                line.append(i)
            for j, col in enumerate(self._ndxMap):
                if j is not self._indexCol:
                    line.append(self._getLocalColumn(j)[i])
            top.append(line)

        bottom = []
        for i in range(len(self._getLocalColumn(0))-4, len(self._getLocalColumn(0))):
            line = []
            if self._index is not None:
                line.append(self._index[i])
            else:
                line.append(i)
            for j, col in enumerate(self._ndxMap):
                if j is not self._indexCol:
                    line.append(self._getLocalColumn(j)[i])
            bottom.append(line)


        #construct lines from header lines, top and bottom

        if self._indexCol is not None:
            headerline = str(self._seriesHeaders[self._indexCol]) + ', '
        else:
            headerline = ''
        for j, col in enumerate(headerlines):
            if j is self._indexCol:
                pass
            elif j is not len(self._seriesHeaders)-1:
                headerline += str(col) + ', '
            else:
                headerline += str(col) + '\n'

        datalines = ''
        for dataline in top:
            dline = ''
            for j, data in enumerate(dataline):
                if j is not len(dataline)-1:
                    dline += str(data) + ', '
                else:
                    dline += str(data) + '\n'
            datalines += dline

        for x in range(0,3):
            datalines += '\t\t.\n'


        for dataline in bottom:
            dline = ''
            for j, data in enumerate(dataline):
                if j is not len(dataline)-1:
                    dline += str(data) + ', '
                else:
                    dline += str(data) + '\n'
            datalines += dline

        template = template.format(mdlines, headerline, datalines)

        return template

    """
    Overloaded [] operators
    """
    def __getitem__(self, arg):
        globalNdx = None
        if type(arg) is type("string"):
            globalNdx = self._getGlobalColumnFromName(arg)
            vals = self._getLocalColumn(globalNdx)
            # construct new time series
            return TimeSeries(values=vals, index=self._index, dtype=type(vals[0]))




    '''
    ---- Private Functions -----------------
    '''

    def _getGlobalColumnFromName(self, colname):
        try:
            for ndx, header in enumerate(self.seriesHeaders):
                if colname in header:
                    return ndx
            raise Exception("Series '" + colname + "' not found in dataset." )
        except Exception:
            raise

    def _getLocalColumn(self, globalndx):
        map = self._ndxMap[globalndx]

        if map[0] == 'object':      return self._addtlCols[map[1]]
        elif map[0] == 'float':     return self._floatCols[map[1]]
        elif map[0] == 'int':       return self._intCols[map[1]]
        elif map[0] == 'datetime':  return self._timeCols[map[1]]

        return None

    def _detectDatatypes(self, colmjr):
        localindexes = {"dt":0, "int":0, "other":0, "float":0}
        self._floatCols = np.empty((0, colmjr.shape[1]), dtype='float')
        self._intCols = np.empty((0, colmjr.shape[1]), dtype='int')
        self._timeCols = np.empty((0, colmjr.shape[1]), dtype='datetime64')
        self._addtlCols = np.empty((0, colmjr.shape[1]), dtype='object')
        # detect datatypes
        for i, col in enumerate(colmjr):
            try: #floats
                col = col.astype(float)
                self._floatCols = np.vstack([self._floatCols, col])

                # manage global ndexing
                self._ndxMap.append(('float', localindexes['float']))
                localindexes['float'] += 1
            except: #ints
                try:
                    col = col.astype(int)
                    self._intCols = np.vstack([self._intCols, col])

                    self._ndxMap.append(('int', localindexes['int']))
                    localindexes['int'] += 1
                except:
                    try: #datetime
                        col = col.astype('datetime64')
                        self._timeCols = np.vstack([self._timeCols, col])

                        self._ndxMap.append(('datetime', localindexes['dt']))
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

                            self._ndxMap.append(('datetime', localindexes['dt']))
                            localindexes['dt'] += 1
                        except: #all others
                            self._addtlCols = np.vstack([self._addtlCols, col])

                            self._ndxMap.append(('object', localindexes['other']))
                            localindexes['other'] += 1

        if localindexes['dt'] is 0:
            traceback.print_exc(file=sys.stdout)
            print("\n---------------------------------\n")
            print('''
Warning: Could not automatically detect or convert datetime column.
Please convert manually with dataset[<col_number or column_name>].isDateTime(<format>).
            ''')


    def renameSeriesHeaders(self, arg):
        newHeaders = []

        if type(arg) is type({}):
            for header in self.seriesHeaders:
                if header in map:
                    newHeaders.append(map[header])
                else:
                    newHeaders.append(map[header])
            self.seriesHeaders = np.array(newHeaders)

        elif type(arg) is type([]):
            self.seriesHeaders = np.array(arg)

        return self

    def genHeadersFromMetadataRows(self, rows):
        newHeaders = []
        for i, row in enumerate(self._headerMetadata):
            header = ''
            if i in rows:
                for j, col in enumerate(row):
                    if len(newHeaders) < len(row):
                        newHeaders.append(col)
                    else:
                        newHeaders[j] += '_'+col

        print(newHeaders)

        self.seriesHeaders = np.array(newHeaders)


    # deferred execution
    def _reverseExecute(self):
        for f in self._callChain:
            f()




'''
The class which contains the library itself.
'''
