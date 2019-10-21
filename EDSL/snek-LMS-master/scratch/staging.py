#/usr/bin/python3

import sys
import ast
import types
import parser
import inspect
import builtins
import astunparse

var_names = {}

def freshName(s = ""):
    global var_names
    if s not in var_names:
        var_names[s] = 0
    var_names[s] += 1
    return "{0}${1}".format(s, var_names[s])

class ConditionRepChecker(ast.NodeVisitor):
    def __init__(self, reps):
        self.reps = reps
        self.hasRep = False
        super()

    def visit_Name(self, node):
        # print("-------Name-------")
        if node.id == "RepString" or node.id == "RepInt":
            self.hasRep = True

def vIf(test, body, orelse, reps):
    # print("----------IF----------")
    if(isinstance(test, bool)):
        # print("No rep")
        if(test):
            # print(ast.dump(body()))
            # print("True")
            res = body()
            return res
        else:
            # print(type(orelse))
            # print(ast.dump(orelse()))
            # print("False")
            # print(orelse())
            res = orelse()
            return res
            # return orelse()
    else:
        return IRIf(test, body, orelse)
    # print("--------End IF--------")

def __ret(value):
    return IRRet(value)

def parameterized(dec):
    def layer(*args, **kwargs):
        def repl(f):
            return dec(f, *args, **kwargs)
        return repl
    return layer

def getClass(cls_name, mod_name = __name__):
    """
    Get Class definition from module, current module by default
    """
    modl = sys.modules[mod_name]
    Cls = getattr(modl, cls_name)
    return Cls

def getFunRepAnno(f):
    if isinstance(f, types.FunctionType):
        mod_ast = ast.parse(inspect.getsource(f))
        assert(isinstance(mod_ast, ast.Module))
        funcdef_ast = mod_ast.body[0] #TODO: always get the first one?
        assert(isinstance(funcdef_ast, ast.FunctionDef))
        return getFunRepAnno(funcdef_ast)

    if isinstance(f, ast.FunctionDef):
        ann_args = list(filter(lambda a: a.annotation, f.args.args))
        return dict(list(map(lambda a: (a.arg, a.annotation.id), ann_args)))

    raise NotImplementedError(f.__name__)

################################################

class IR(object): pass

class IRDef(IR):
    def __init__(self, name, args, body):
        self.name = name
        self.args = args
        self.body = body

class IRConst(IR):
    def __init__(self, v):
        self.v = v

class IRInt(IR):
    def __init__(self, n):
        self.n = n

class IRIntAdd(IR):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

class IRIntSub(IR):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

class IRIntMul(IR):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

class IRIntEq(IR):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

class IRIf(IR):
    def __init__(self, cnd, thn, els):
        self.cnd = cnd
        self.thn = thn
        self.els = els

class IRWhile(IR):
    def __init__(self, cnd, body):
        self.cnd = cnd
        self.body = body

class IRRet(IR):
    def __init__(self, val):
        self.val = val

__if = IRIf
__while = IRWhile
__return = IRRet

################################################

class CodeGen(object): pass

class PyGenIRDef(object):
    def gen(self, irdef):
        bodycode = PyCodeGen(irdef.body).gen()
        return "def {0}({1}): return {2}".format(irdef.name, ",".join(irdef.args), bodycode)

class PyGenIRConst(object):
    def gen(self, irconst): return str(irconst.v)

class PyGenIRInt(object):
    def gen(self, irint):
        return str(irint.n)

class PyGenRepInt(object):
    def gen(self, irint):
        return str(irint.n)

class PyGenInt(object):
    def gen(self, n):
        return str(n)

class PyGenIRIntAdd(object):
    def gen(self, iradd):
        lhscode = PyCodeGen(iradd.lhs).gen()
        rhscode = PyCodeGen(iradd.rhs).gen()
        return "{0} + {1}".format(lhscode, rhscode)

class PyGenIRIntSub(object):
    def gen(self, irsub):
        lhscode = PyCodeGen(irsub.lhs).gen()
        rhscode = PyCodeGen(irsub.rhs).gen()
        return "{0} - {1}".format(lhscode, rhscode)

class PyGenIRIntMul(object):
    def gen(self, irmul):
        # print(irmul.lhs)
        # print(irmul.rhs)
        lhscode = PyCodeGen(irmul.lhs).gen()
        rhscode = PyCodeGen(irmul.rhs).gen()
        return "{0} * {1}".format(lhscode, rhscode)

class PyGenIRIf(object):
    def gen(self, irif):
        # print(irif.cnd)
        # print(irif.thn)
        # print(irif.els)
        cond = PyCodeGen(irif.cnd).gen()
        thn = PyCodeGen(irif.thn()).gen()
        els = PyCodeGen(irif.els()).gen()
        return """
if {0}:
    {1}
else:
    {2}
        """.format(cond, thn, els)

class PyGenIRReturn(object):
    def gen(self, irret):
        # print("ret:{0}\n".format(irret.val))
        val = PyCodeGen(irret.val).gen()
        return "return {0}".format(val)

class PyGenIRIntEq(object):
    def gen(self, ireq):
        lhscode = PyCodeGen(ireq.lhs).gen()
        rhscode = PyCodeGen(ireq.rhs).gen()
        return "{0} == {1}".format(lhscode, rhscode)

class PyCodeGen(CodeGen):
    def __init__(self, ir):
        self.ir = ir
        # print("self.ir = {0}".format(self.ir))

    def gen(self):
        n = type(self.ir).__name__
        nm = n[0].upper()
        nmm = nm + n[1:]
        clsName = "PyGen{0}".format(nmm)
        Cls = getClass(clsName)
        return Cls().gen(self.ir)

    def ast(self):
        return ast.parse(self.gen())

    def dumpast(self):
        return ast.dump(self.ast())

class CCodeGen(CodeGen): pass

class SchemeGenIRDef(object):
    def gen(self, irdef):
        bodycode = SchemeCodeGen(irdef.body).gen()
        return "(define ({0} {1}) {2})".format(irdef.name, " ".join(irdef.args), bodycode)

class SchemeGenIRConst(object):
    def gen(self, irconst): return str(irconst.v)

class SchemeGenIRInt(object):
    def gen(self, irint): return str(irint.n)

class SchemeGenIRIntAdd(object):
    def gen(self, iradd):
        lhscode = SchemeCodeGen(iradd.lhs).gen()
        rhscode = SchemeCodeGen(iradd.rhs).gen()
        return "(+ {0} {1})".format(lhscode, rhscode)

class SchemeGenIRIntMul(object):
    def gen(self, irmul):
        lhscode = SchemeCodeGen(irmul.lhs).gen()
        rhscode = SchemeCodeGen(irmul.rhs).gen()
        return "(* {0} {1})".format(lhscode, rhscode)

class SchemeCodeGen(CodeGen):
    def __init__(self, ir):
        self.ir = ir

    def gen(self):
        clsName = "SchemeGen{0}".format(type(self.ir).__name__)
        Cls = getClass(clsName)
        return Cls().gen(self.ir)

################################################

class RepTyp(object): pass

#class RepInt(RepTyp, metaclass=RepTyp):
class RepInt(RepTyp):
    def __init__(self, n):
        self.n = n
    def __IR__(self):
        if isinstance(self.n, int): return IRConst(self.n)
        else: return IRInt(self.n)
    def __add__(self, m):
        if isinstance(m, RepTyp): m = m.__IR__()
        return IRIntAdd(self.__IR__(), m)
    def __sub__(self, m):
        if isinstance(m, RepTyp): m = m.__IR__()
        return IRIntSub(self.__IR__(), m)
    def __mul__(self, m):
        if isinstance(m, RepTyp): m = m.__IR__()
        return IRIntMul(self.__IR__(), m)
    def __eq__(self, m):
        if isinstance(m, RepTyp): m = m.__IR__()
        return IRIntEq(self.__IR__(), m)
class RepStr(RepTyp): pass

################################################

class StagingRewriter(ast.NodeTransformer):
    """
    StagingRewriter does two things:
    1) lift next-stage variables to be Rep
    2) virtualize primitives such as `if`, `while`, `for` and etc
    Note: Probably we may also rewrite operators such as `+` rather than overloading them.
    """
    def __init__(self, reps = {}):
        self.reps = reps
        super()
    def visit_If(self, node):
        # TODO: Virtualization of `if`
        # If the condition part relies on a staged value, then it should be virtualized.
        # print(ast.dump(node))

        # if node is of the form (test, body, orelse)

        # iter_fields lets me iterate through the contents of the if node
        # gives the child as a tuple of the form (child-type, object)
        # cond_node = node.test;
        # check for BoolOp and then Compare
        # node.body = list(map(lambda x: self.generic_visit(x), node.body))
        self.generic_visit(node)

        # vIf(node.test, node.body, node.orelse, self.reps)
        tBranch_name = freshName("then")
        eBranch_name = freshName("else")
        tBranch = ast.FunctionDef(name=tBranch_name,
                                  args=ast.arguments(args=[], vararg=None, kwonlyargs=[], kwarg=None, defaults=[], kw_defaults=[]),
                                  body=node.body,
                                  decorator_list=[])
        eBranch = ast.FunctionDef(name=eBranch_name,
                                  args=ast.arguments(args=[], vararg=None, kwonlyargs=[], kwarg=None, defaults=[], kw_defaults=[]),
                                  body=node.orelse,
                                  decorator_list=[])
        ast.fix_missing_locations(tBranch)
        ast.fix_missing_locations(eBranch)

        self.generic_visit(tBranch)
        self.generic_visit(eBranch)

        # self.vIf(node.test, tBranch, eBranch)
        # print(node.lineno)
        # new_node = ast.Expr(ast.Call(func=ast.Name(id='__return', ctx=ast.Load()), args=[
        #     ast.Call(
        #     func=ast.Name(id='vIf', ctx=ast.Load()),
        #     args=[node.test,
        #           ast.Name(id=tBranch_name, ctx=ast.Load()),
        #           ast.Name(id=eBranch_name, ctx=ast.Load()),
        #           ast.Dict(list(map(ast.Str, self.reps.keys())),
        #                    list(map(ast.Str, self.reps.values()))),
        #          ],
        #     keywords=[]
        # )], keywords=[]))

        new_node = ast.Return(value=ast.Call(
            func=ast.Name(id='vIf', ctx=ast.Load()),
            args=[node.test,
                  ast.Name(id=tBranch_name, ctx=ast.Load()),
                  ast.Name(id=eBranch_name, ctx=ast.Load()),
                  ast.Dict(list(map(ast.Str, self.reps.keys())),
                           list(map(ast.Str, self.reps.values()))),
                 ],
            keywords=[]
        ))

        ast.fix_missing_locations(new_node)
        # self.generic_visit(new_node)
        mod = [tBranch, eBranch, new_node]
        # print(ast.dump(eBranch))
        return mod
        #return ast.copy_location(mod, node)

    def visit_While(self, node):
        # TODO: Virtualization of `while`
        self.generic_visit(node)
        return node # COMMENT WHEN __while IS DONE

        # UNCOMMENT WHEN __while IS DONE
        # nnode = ast.copy_location(ast.Call(func=ast.Name('__while', ast.Load()),
        #                                 args=[node.test, node.body],
        #                                 keywords=[]),
        #                         node)
        # nnode.parent = node.parent
        # return nnode

    def visit_FunctionDef(self, node):
        self.reps = getFunRepAnno(node)
        self.generic_visit(node)
        node.decorator_list = [] # Drop the decorator
        # print(node.name)
        return node

    def visit_Return(self, node):
        self.generic_visit(node)
        return node

        # ret_name = freshName("ret")
        # retfun = ast.FunctionDef(name=ret_name,
        #                           args=ast.arguments(args=[], vararg=None, kwonlyargs=[], kwarg=None, defaults=[], kw_defaults=[]),
        #                           body=[node],
        #                           decorator_list=[])

        # ast.fix_missing_locations(retfun)
        # retnode = ast.Expr(ast.Call(func=ast.Name('__return', ast.Load()),
        #                                 args=[ast.Name(id=ret_name, ctx=ast.Load())],
        #                                 keywords=[]))
        # ast.fix_missing_locations(retnode)
        # # ast.copy_location(retnode, node)
        # return [retfun, retnode]
        # return retnode

    def visit_Name(self, node):
        self.generic_visit(node)
        if node.id in self.reps:
            nnode = ast.copy_location(ast.Call(func=ast.Name(id=self.reps[node.id], ctx=ast.Load()),
                                              args=[ast.Str(s=node.id)],
                                              keywords=[]),
                                    node)
            return nnode
        return node

    def visit_Continue(self, node):
        print("Cont: {}".format(ast.dump(node)))
        self.generic_visit(node)

def lms(obj):
    """
    Rep transforms the AST to annotated AST with Rep(s).
    TODO: What about Rep values defined inside of a function, rather than as an argument?
    TODO: How to lift constant value?
    TODO: How to handle `return`
    TODO: Handle sequence and side effects
    TODO: Assuming that there is no free variables in the function
    """
    if isinstance(obj, types.FunctionType):
        func = obj
        mod_ast = ast.parse(inspect.getsource(func))

        print(ast.dump(mod_ast))

        # GW: do you want to compare unfix/fix version of new_mod_ast?
        #     rather than mod_ast vs new_mod_ast
        # print("before modding, ast looks like this:\n\n{0}".format(ast.dump(mod_ast)))
        # print("========================================================")

        # for node in ast.walk(mod_ast):
        # print("\n{0}\n".format(ast.dump(mod_ast)))
            # for child in ast.iter_child_nodes(node):
            #     child.parent = node

        new_mod_ast = StagingRewriter().visit(mod_ast)
        ast.fix_missing_locations(new_mod_ast)
        # print(astunparse.dump(new_mod_ast))
        # print("===========================AFTER==================\n\n")

        # for node in ast.walk(mod_ast):
        # print("\n{0}\n".format(ast.dump(mod_ast)))
        # print("\n{0}\n".format(ast.dump(new_mod_ast)))

        # print("after modding, ast looks like this:\n\n{0}\n\n".format(ast.dump(new_mod_ast)))

        exec(compile(new_mod_ast, filename="<ast>", mode="exec"), globals())
        return eval(func.__name__)
    elif isinstance(obj, types.MethodType):
        return NotImplemented
    else: return NotImplemented

@parameterized
def Specialize(f, Codegen, *args, **kwargs):
    """
    Specialize transforms the annotated IR to target language.
    Note: f must be a named function
    TODO: f's argument names may different with variables in the inner body
    """
    fun_name = f.__name__
    fun_args = inspect.getfullargspec(f).args
    rep_anno = getFunRepAnno(f)
    rep_args = [getClass(rep_anno[farg])(farg) for farg in fun_args]
    irbody = f(*rep_args)
    codegen = Codegen(IRDef(fun_name, fun_args, irbody))
    codestr = codegen.gen()
    print(codestr)
    # from py_to_sexpr import sexp
    # q = ast.parse(codestr)
    # exec(compile(q, filename="<ast>", mode="exec"), globals())
    # sexp(q) #TODO: need to turn this into a function
    # exec(codestr, globals())
    # return eval(fun_name)

################################################

def giveBack(x):
    return x

"""
TODO: User can provide return type.
TODO: User can even provide return type as union;
      eg, power(b: RepInt, x) -> RepInt | RepStr
"""
# @lms
# def power(b : RepInt, x) -> RepInt:
#     if (x == 0): return 1
#     else: return b * power(b, x-1)

# @lms
# def zero(x):
#     if (x == 0): return 1
#     else: return 0

# @lms
# def multiply(x : RepInt, n) -> RepInt:
#     if n == 1: return x
#     else: return x + multiply(x, n - 1)

# @lms
# def test(x : RepInt) -> RepInt:
#     if (x == 2):
#         return x + 1
#     else:
#         return x + 2

@lms
def test(x: RepInt) -> RepInt:
    while(True):
        continue

"""
Ideally, user could specify different code generators for different targer languages.
The code generator translates IR to string representation of target language.
"""
@Specialize(PyCodeGen)
def snippet1(b: RepInt):
    return power(b, 3)

# assert(snippet(3) == 27) # Here we can just use snippet

# """
# Explaination: decorating `snippet` with @Specialize is equivalent to:
# """
# def snippet2(b : RepInt): return stagedPower(b, 3)
# power3 = Specialize(PyCodeGen)(snippet2)
# assert(power3(3) == 27)

