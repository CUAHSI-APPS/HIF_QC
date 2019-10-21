__all__ = [
    'reflect', 'reify', 'fresh',
    'Rep', 'reflectDef', 'Tensor', 'Tuple',
    'NonLocalReturnValue', 'NonLocalBreak', 'NonLocalContinue',
    '_if', '_while', '_def_staged', '_call_staged', '_return', '_print', '_printf',
    '_var', '_assign', '_read', '_len',
    '_break', '_continue', '_for', '_stageLambda'
]


var_counter = 0
in_staging = False


def freshName(): # for generating AST
    global var_counter
    n_var = var_counter
    var_counter += 1
    return "v" + str(n_var)

stFresh = 0
stBlock = []
stFun   = []
def run(f):
    global stFresh, stBlock, stFun
    sF = stFresh
    sB = stBlock
    sN = stFun
    try:
        return f()
    finally:
        stFresh = sF
        stBlock = sB
        stFun = sN

def fresh():
    global stFresh
    stFresh += 1
    return Rep("x"+str(stFresh-1))

def reify(f, *args):
    def f1():
        global stBlock
        stBlock = ['begin']
        try:
            last = f(*args)
            return stBlock + [ last ]
        except NonLocalReturnValue as e:
            raise NonLocalReturnValue(stBlock + [e.value]) # propagate exception ...
    return run(f1)

def reflect(s):
    global stBlock
    id = fresh()
    stBlock += [["let", id, s]]
    return id

class Rep(object):
    def __init__(self, n, *dims):
        self.n = n
        self.dims = dims
    def __add__(self, m):
        return reflect(["+",self,m])
    def __radd__(self, m):
        return reflect(["+",m,self])
    def __sub__(self, m):
        return reflect(["-",self,m])
    def __mul__(self, m):
        return reflect(["*",self,m])
    def __rmul__(m, self):
        return reflect(["*",m,self])
    def __truediv__(self, m):
        return reflect(["/",self,m])
    def __rtruediv__(self, m):
        return reflect(["/",m,self])
    def __mod__(self, m):
        return reflect(["%",self,m])
    def __eq__(self, m):
        return reflect(["==",self,m])
    def __ne__(self, m):
        return reflect(["!=",self,m])
    def __le__(self, m):
        return reflect(["<=",self,m])
    def __lt__(self, m):
        return reflect(["<",self,m])
    def __ge__(self, m):
        return reflect([">=",self,m])
    def __gt__(self, m):
        return reflect([">",self,m])
    def __repr__(self):
        return str(self.n)

    # RepFunction
    def __call__(self,*args):
        # TODO
        return reflect(['call', self,[','.join([str(a) for a in args])]])

    ## Tensor Functions
    def __getitem__(self, i):
        return reflect(["array-get",self,i])
    def __setitem__(self,i,v):
        return reflect(["array-set",self,i,v])
    @property
    def data(self):
        return reflect(["getattr",self,"data"])
    @data.setter
    def data(self, v):
        return reflect(["setattr",self,"data",v])
    def data_get(self, i):
        return reflect(["array-get",self,"data",i])
    def data_set(self, i, v):
        return reflect(["array-set",self,"data",i,v])
    def dot(self, t):
        return reflect(["dot",self,t])
    def item(self):
        return reflect(['array-get',self,0])

    ## Tuple Functions
    @property
    def _1(self):
        return reflect(["getattr",self,"_1"])
    @property
    def _2(self):
        return reflect(["getattr",self,"_2"])
    @property
    def _3(self):
        return reflect(["getattr",self,"_3"])

    def __getattr__(self, name):
        def wrapper(*args, **kwargs):
            return reflect(["call",self,name,' '.join([str(a) for a in args]),' '.join(['{}={}'.format(str(a),str(kwargs[a])) for a in kwargs])])
        return wrapper

def Tensor(*dims):
    tmp = reflect(["call","tensor",[*dims]])
    return Rep(tmp.n, dims)

def Tuple(*args):
    tmp = reflect(["call","tuple",[*args]])
    return Rep(tmp.n)

class NonLocalReturnValue(Exception):
    def __init__(self, value):
        self.value = value

def _return(value):
    raise NonLocalReturnValue(value)

class NonLocalBreak(Exception): pass
class NonLocalContinue(Exception): pass

def _stageLambda(l):
    z = fresh()
    return reflect(['lambda',z,reify(l, z)])

def _break(): raise NonLocalBreak()
def _continue(): raise NonLocalContinue()

def _print(value): # TODO HACK!
    if not isinstance(value, Rep) and not in_staging:
        print(value)
        return
    if isinstance(value, str):
        return reflect(["print", '"{}"'.format(value)])
    else:
        return reflect(["print", value])

def reflectDef(name, args, f):
    global stBlock
    id = fresh()
    stBlock += [["def", name, args, f]]
    return id

def _def_staged(f, *args):
    nargs = [fresh() for _ in args]
    return reflectDef(f.__name__, nargs, reify(f, *nargs))

def _call_staged(f, *args):
    return reflect(['call', f.__name__, *args])

def _printf(s, vs):
    nvs = ['"{}"'.format(i) if isinstance(i, str) else '{}'.format(i) for i in vs]
    return reflect(["printf", ['"{}"'.format(s), "{}".format(", ".join(nvs))]])

def _var():
    return reflect(["new"])

# env = {}

def _assign(name, value):
    return reflect(["set", name, value])

def _read(name):
    return reflect(["get", name])

def _len(name):
    # if not isinstance(name, Rep):
        # return len(name)
    return reflect(["len", name])

def _if(test, body, orelse):
    global in_staging
    if not isinstance(test, Rep):
        if test:
            return body()
        else:
            return orelse()
    else:
        curr_in_staging = in_staging
        in_staging = True
        # There's a little bit of complication dealing with
        # _return: we currently require that either both
        # of the if branches _return, or none of them.
        def capture(f):
            try: return (False, reify(f))
            except NonLocalReturnValue as e:
                return (True, e.value)
        thenret, thenp = capture(body)
        # if len(thenp) > 1:
        #     thenp.insert(0, "begin")
        elseret, elsep = capture(orelse)
        # if len(elsep) > 1:
        #     elsep.insert(0, "begin")
        rval = reflect(["if", test, thenp, elsep])
        in_staging = curr_in_staging
        if thenret & elseret:
            raise NonLocalReturnValue(rval) # proper return
        elif (not thenret) & (not elseret):
            return rval
        else:
            raise Exception("if/else: branches must either both return or none of them")

def _while(test, body):
    global in_staging
    # We don't currently support return inside while
    def capture(f):
        try: return (False, reify(f))
        except NonLocalReturnValue as e:
            return (True, e.value)
        except NonLocalContinue as e:
            return (False, __while(test, f)) #f must be body if we hit a continue

    ttest = test()
    if not isinstance(ttest, Rep):
        while ttest or test(): # protects against side-effects
            try:
                ttest = False
                body()
            except NonLocalBreak as e:
                return None
            except NonLocalReturnValue as e:
                return e.value
            except NonLocalContinue as e:
                pass
        return

    curr_in_staging = in_staging
    in_staging = True
    # no way to protect against side-effect in gen code other than removing
    # ttest's generated code in post-processing
    testret, testp = capture(test)
    bodyret, bodyp = capture(body)
    rval = reflect(["while", testp, bodyp])
    in_staging = curr_in_staging
    if (not testret) & (not bodyret):
        return rval
    else:
        raise Exception("while: return in body not allowed")

def _for(it, body):
    global in_staging
    if not isinstance(it, Rep):
        for i in it:
            try:
                body(i)
            except NonLocalBreak as e:
                return None
            except NonLocalReturnValue as e:
                return e.value
            except NonLocalContinue as e:
                pass
        return

    def capture(f, i):
        try: return (False, reify(f, i))
        except NonLocalReturnValue as e:
            return e.value

    curr_in_staging = in_staging
    in_staging = True
    i = fresh()
    bodyret, bodyp = capture(body, i)
    rval = reflect(["for", i, it, bodyp])
    in_staging = False
    if not bodyret:
        return rval
    else:
        raise Exception("for: return in body not allowed")
