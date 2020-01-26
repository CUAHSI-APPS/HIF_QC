# taking the lead from pandas,
#  internal arrays are numpy representations
import numpy as np
import builtins
import traceback
import sys
import math
import pandas as pd
from datetime import datetime
from dateutil.parser import parse
from inspect import getsource, getargspec
from copy import deepcopy


supress = True




class Value():
    def __init__(self, valueNdx=None, context=None, currentValue=None, dt=None, scalar=True, timestep=None):
        self._valueIndex = valueNdx
        self._dt = dt
        self._context = context
        self.value = currentValue
        self._scalar = scalar
        self._timedelta = timestep


    def isnan(self):
        return math.isnan(self.value)

    def isScalar(self):
        return self._scalar

    def intIndex(self):
        return self._valueIndex

    def dateTimeIndex(self):
        return self._dt

    def prior(self, num):
        if (self._valueIndex - num) < 0:
            sublist = np.empty([0])
            if not supress:
                print("Warning: Value.prior() specified number out of bounds, empty array returned.")
        else:
            sublist = self._context[self._valueIndex-num:self._valueIndex]
        return Value(self._valueIndex-num, sublist, self.value, self._dt, False, timestep=self._timedelta)


    """
    Overloaded Operators
    """
    def __getitem__(self, key):
        if type(key) is type(0) and self._scalar is False:
            if len(self._context) <= key:
                return self
            return Value(self._valueIndex + key, self._context, self._context[key], self._dt, True, timestep=self._timedelta)

    def __contains__(self, key):
        pass

    def __add__(self, other):
        if type(self) is type(other):
            return self._mathOrganizer(self, other, '+')
        else:
            if type(other) is not type("") and type(other) is not type({}):
                return self.value + other

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if type(self) is type(other):
            return self._mathOrganizer(self, other, '-')
        else:
            if type(other) is not type("") and type(other) is not type({}):
                return self.value - other

    def __rsub__(self, other):
        if type(self) is type(other):
            return self._mathOrganizer(other, self, '-')
        else:
            if type(other) is not type("") and type(other) is not type({}):
                return other - self.value

    def __mul__(self, other):
        if type(self) is type(other):
            return self._mathOrganizer(self, other, '*')
        else:
            if type(other) is not type("") and type(other) is not type({}):
                return self.value * other

    def __rmul__(self, other):
        return self.__mul__(other)

    def __div__(self, other):
        if type(self) is type(other):
            return self._mathOrganizer(self, other, '/')
        else:
            if type(other) is not type("") and type(other) is not type({}):
                return self.value / other

    def __rdiv__(self, other):
        if type(self) is type(other):
            return self._mathOrganizer(other, self, '/')
        else:
            if type(other) is not type("") and type(other) is not type({}):
                return self.value / other

    # overloaded comparision operators
    def __gt__(self, other):

        if type(self) is type(other):
            return self._comparisionOrganizer(other, ">")
        else:
            if type(other) is not type("") and type(other) is not type({}):
                return self.value > other

    def __ge__(self, other):
        if type(self) is type(other):
            return self._comparisionOrganizer(other, ">=")
        else:
            if type(other) is not type("") and type(other) is not type({}):
                return self.value >= other

    def __lt__(self, other):
        if type(self) is type(other):
            return self._comparisionOrganizer(other, "<")
        else:
            if type(other) is not type("") and type(other) is not type({}):
                return self.value < other

    def __le__(self, other):
        if type(self) is type(other):
            return self._comparisionOrganizer(other, "<=")
        else:
            if type(other) is not type("") and type(other) is not type({}):
                return self.value <= other

    def __ne__(self, other):
        if type(self) is type(other):
            return self._comparisionOrganizer(other, "!=")
        else:
            if type(other) is not type("") and type(other) is not type({}):
                return self.value != other

    def __eq__(self, other):
        if type(self) is type(other):
            return self._comparisionOrganizer(other, "==")
        else:
            if type(other) is not type("") and type(other) is not type({}):
                return self.value == other

    def __str__(self):
        if self._scalar is True:
            return str(self.value)
        else:
            return np.array2string(self._context)

    """
----Private functions------------
    """
    def _mathOrganizer(self, lhs, rhs, op):
        if op == "-" or op == "/":
            if lhs._scalar is True and rhs._scalar is False:
                raise Exception('''
Cannot subtract or divide a vector or list from a scalar.
                ''')

        if lhs._scalar is True and rhs._scalar is True:
            return self._scalarOp(lhs.value, rhs.value, op)
        elif lhs._scalar is True and rhs._scalar is False:
            return self._scalarListOp(lhs.value, rhs._context, op)
        elif lhs._scalar is False and rhs._scalar is True:
            return self._scalarListOp(rhs.value, lhs._context, op)

        else:
            raise Exception('''
Error: No operation defintion exists for list value {} list value within test scope.
        '''.format(op))

    def _comparisionOrganizer(self, other, cmp):
        if self._scalar is True and other._scalar is True:
            return self._scalarCmp(self.value, other.value, cmp)
        elif self._scalar is True and other._scalar is False:
            return self._scalarListCmp(self.value, other._context, cmp)
        elif self._scalar is False and other._scalar is True:
            return self._scalarListCmp(other.value, self._context, cmp)
        else:
            return self._listListCmp(other.value, self._context, cmp)


    def _scalarOp(self, lhs, rhs, op):
        if op is "+":
            return lhs + rhs
        if op is "-":
            return lhs - rhs
        if op is "*":
            return lhs * rhs
        if op is "/":
            return lhs / rhs

    def _scalarListOp(self, s1, l1, op):
        if op is "+":
            lr = []
            for s in l1:
                lr.append(s+s1)
            return lr
        if op is "-":
            lr = []
            for s in l1:
                lr.append(s-s1)
            return lr
        if op is "*":
            lr = []
            for s in l1:
                lr.append(s*s1)
            return lr
        if op is "/":
            lr = []
            for s in l1:
                lr.append(s/s1)
            return lr

    def _scalarCmp(self, s1, s2, cmp):
        if cmp is "==":
            return s1 == s2
        if cmp is "<":
            return s1 < s2
        if cmp is ">":
            return s1 > s2
        if cmp is ">=":
            return s1 >= s2
        if cmp is "<=":
            return s1 <= s2
        if cmp is "!=":
            return s1 != s2
        pass

    """
    Function: _scalarListCmp
    Desc: Performs pairwise compairisions of l1 against s1. If any pair fails this
        comparision then the entire function returns false. Otherwise it returns true.
        Generally we want to flag when function returns true.
    """
    def _scalarListCmp(self, s1, l1, cmp):
        if l1.size is 0:
            return False
        elif cmp == "==":
            for val in l1:
                if s1 != val:
                    return False
            return True
        elif cmp == "<":
            for val in l1:
                if s1 >= val:
                    return False
            return True
        elif cmp == ">":
            for val in l1:
                if s1 <= val:
                    return False
            return True
        elif cmp == ">=":
            for val in l1:
                if s1 < val:
                    return False
            return True
        elif cmp == "<=":
            for val in l1:
                if s1 > val:
                    return False
            return True
        elif cmp == "!=":
            for val in l1:
                if s1 == val:
                    return False
            return True

    def _listListCmp(self, l1, l2, cmp):
        if cmp is "==":
            if l1 is l2:
                return True
            for val_a in l1:
                for val_b in l2:
                    if val_a != val_b:
                        return False
            return True

        elif cmp == "<":
            for val_a in l1:
                for val_b in l2:
                    if val_a >= val_b:
                        return False
            return True

        elif cmp == ">":
            for val_a in l1:
                for val_b in l2:
                    if val_a <= val_b:
                        return False
            return True

        elif cmp == ">=":
            for val_a in l1:
                for val_b in l2:
                    if val_a < val_b:
                        return False
            return True

        elif cmp == "<=":
            for val_a in l1:
                for val_b in l2:
                    if val_a > val_b:
                        return False
            return True

        elif cmp == "!=":
            if len(l1) != len(l2):
                return true
            for i, val_a in enumerate(l1):
                for val_b in l2:
                    if val_a == val_b:
                        return False
            return True



'''
Name: Flag
Description: An object which holds metadata about a flagged datapoint.
Private Members: Flag code, test Parameters/defintion
'''
class Flag():
    def __init__(self, code, noneCode, timestamp=None):
        self._codes = [code]
        self._noneCode = noneCode
        self._timestamp = timestamp

    def __iadd__(self, other):
        return __add__(other)

    def __add__(self, other):
        if self._codes == other._codes:
            return self._codes

        elif len(self._codes) is 1 and self._noneCode in self._codes:
            return Flag(other._codes, other._noneCode, other._timestamp)

        elif (self._noneCode not in self._codes and
         other._noneCode not in other._codes):
            tmp = deepcopy(self._codes)
            for c in other._codes:
                tmp.append(c)
            return tmp


    def addCode(self, code):
        # if we only have noneCode
        if len(self._codes) is 1 and self._noneCode in self._codes:
            self._codes[0] = code
        if code in self._codes:
            return
        if code is self._noneCode:
            return
        else:
            self._codes.append(code)

    def isFlag(self, flag):
        if flag in self._codes:
            return True
        return False

    def notNone(self):
        if self._noneCode in self._codes:
            return False
        return True

    def __str__(self):
        if len(self._codes) is 1:
            return str(self._codes[0])
        return str(self._codes)

'''
Name: TimeSeries
Description: Core data structure. Contains one vector and one TimeSeries.
'''
class TimeSeries():
    def __init__(self, values=None, index=None, timedelta=None, dtype=None, flagConf=None, flags=None, header=None):
        # check for valid input index
        self._index = np.array(index, dtype='datetime64')
        self._timedelta = None
        self._dtype = dtype
        self._header = header

        # check for valid datatypes
        # throw error if datatype does not match value
        self._values = np.array(values, dtype= 'f8' if (dtype is None) else dtype)
        self._flags = np.zeros_like(values, dtype='object')
        self._flagconf = flagConf
        self._testHist = np.array([], dtype='object')

        self._state = {}




    '''
--- Built In Test Methods ------------------------
    '''

    def reindex(self, timedelta):
        tmp = pd.DataFrame({'dtindex':self._index, 'values': self._values, 'flags':self._flags}, columns=['dtindex','values','flags'])
        td = pd.Timedelta(timedelta)

        tmp = tmp.set_index('dtindex')

        tmp = tmp.reindex(pd.date_range(start=tmp.index[0], end=tmp.index[-1], freq=td))

        self._index = tmp.index.to_numpy()
        self._values = tmp['values'].to_numpy()
        self._flags = tmp['flags'].to_numpy()




    def missingValueTest(self, mvAlias=None):

        if self._timedelta is None:
            raise Exception(
            '''
Error: Cannot test for missing values without defining series timestep length.
Please specify series timestep with <TimeSeries>.timestep().
            '''
            )

        tmp = pd.DataFrame({'dtindex':self._index, 'values': self._values, 'flags':self._flags}, columns=['dtindex','values','flags'])
        td = pd.Timedelta(self._timedelta)

        tmp = tmp.set_index('dtindex')

        tmp = tmp.reindex(pd.date_range(start=tmp.index[0], end=tmp.index[-1], freq=td))

        self._index = tmp.index.to_numpy()
        self._values = tmp['values'].to_numpy()
        self._flags = tmp['flags'].to_numpy()

        missingvals = np.argwhere(np.isnan(self._values))

        if mvAlias is not None:
            missingvals = np.append(missingvals, np.where(self._values == mvAlias))

        for i in missingvals:
            self._flags[i] = Flag(self._flagconf[self._state['flagKey']], self._flagconf['None'])


        return

    """
---- Fluent Syntax Methods ----------------------
    """



    def datapoint(self):
        return self

    def flag(self, arg):
        if self._flagconf is None:
            raise Exception("\nError: No flag codes were defined. Please define a flag code dict with DataSet.flagcodes().are().")
        elif arg not in self._flagconf.keys():
            raise Exception("\nError: Flag code key not found in dataset flag codes. Please ensure that '" + arg + "' exists in dataset flag codes.")
        self._state['flagKey'] = arg
        return self

    def flags(self):
        return self._flags

    def data(self):
        return self._values

    def when(self, funct):
        # this is important for provenance
        self._testHist = np.append(self._testHist, np.array([(self._state['flagKey'], getsource(funct))], dtype=[('test', 'U100'), ('testDef', 'U10000')]))

        iter = False
        if len(getargspec(funct)[0]) > 1:
            if 'i' in getargspec(funct)[0] or 'index' in getargspec(funct)[0]:
                iter = True;


        for i, v in enumerate(self._values):

            val = Value(i, self._values, v, self._index[i], timestep=self._timedelta)

            # switch for additional arguments
            if iter:
                ret = funct(val, i)
            else:
                ret = funct(val)

            if ret is None:
                ret = False

            if ret:
                if self._flags[i] is 0:
                    self._flags[i] = Flag(self._flagconf[self._state['flagKey']], self._flagconf['None'])
                else:
                    self._flags[i].addCode(self._flagconf[self._state['flagKey']])
            else:
                if self._flags[i] is 0:
                    self._flags[i] = Flag(self._flagconf['None'], self._flagconf['None'])

        return self

    def timestep(self, ts):
        self._timedelta = ts
        return self

    def testHistory(self):
        return self._testHist


    """
---- Sugar Functions ------------------------
    """
    def beginning(self, offset=0):
        return self._index[0 + offset]

    def end(self):
        return self._index[len(self._index)-1]

    def value(self):
        return self

    def at(self, arg):
        # reindex if necessary
        if len(self._values) != len(arg._context):
            self.reindex(arg._timedelta)

        if type(arg) is type(Value()):
            return Value(arg._valueIndex, self._values, self._values[arg._valueIndex], arg._dt, timestep=self._timedelta)

        # allow for index or timestamp



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
        self._fp = filePath
        self._headerMetadata = []
        self._timeCols = None
        self._floatCols = None
        self._intCols = None
        self._addtlCols = None
        self._ndxMap = []   #array of tuples mapping global indexes to local indexes
        self._flagCols = None
        self._flagCodes = None

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

    def getFlagCodes(self):
        return self._flagCodes

    def getFlagCode(self, key):
        return self._flagCodes[key]

    def flagcodes(self):
        return self

    def are(self, flag_configs):
        self._flagCodes = flag_configs
        if "None" not in flag_configs:
            self._flagCodes['None'] = 'OK'
            print('''

Warning: Default flag code undefined.
            Set as "OK" by default.
            To override please define a "None" code speficiation in the argument to <dataset>.flagcodes().are({"None":<your value here>}).

''')
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
            return TimeSeries(values=vals, index=self._index, dtype=type(vals[0]), flagConf=self._flagCodes, header=arg)




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

                # replace empties with nan
                for j, f in enumerate(col):
                    if f == '':
                        f = 'nan'
                        col[j] = 'nan'

                col = col.astype(float)
                self._floatCols = np.vstack([self._floatCols, col])

                # manage global ndexing
                self._ndxMap.append(('float', localindexes['float']))
                localindexes['float'] += 1
            except Exception as e: #ints
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
Warning: Could not automatically detect or convert datetime column for dataset from file "{}"
Please convert manually with dataset[<col_number or column_name>].isDateTime(<format>).
            '''.format(self._fp))


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
