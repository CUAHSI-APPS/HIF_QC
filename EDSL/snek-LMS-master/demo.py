from pylms.decorators import *
from pylms.rep import *

@lms
def foo(value):
  my_staged_lambda = __stageLambda(lambda x: x if x > 0 else 0)
  return my_staged_lambda(value)

@stage
def testFoo(x):
  return foo(x)
print(foo.src)
print(testFoo.code)
assert(False)


@lms
def run(x):
  # @rep_fun
  def power(n, k):
    if k == 0:
      return 1
    else:
      return n * power(n, k - 1)
  res = power(x, 4)
  return res

print("======= Original code =======")
print(run.original_src)
print("======= Converted code ========")
print(run.src)
print("\n")

@stage
def runX(x):
  return run(x)

print(runX.Ccode)

# print(run.src)
# print(run(4))
assert(False)

def run(x):
  x = __var()
  def body():
    __assign(x, x - 1)

@lms
def r(x):
  def lifting_param(x):
    if x > 0:
      x = x + 1
    else:
      x = x - 1
    return x
  return lifting_param(x)

print("======= Original code =======")
print(r.original_src)
print("======= Converted code ========")
print(r.src)
val = r(2)
assert(val == 3)
print("\n")

@stage
def runLift(x):
  return r(x)

print("======= SExpr ========")
print(runLift.code)
print("\n")
print("======= C/C++ code ========")
print(runLift.Ccode)
val = runLift(2)
assert(val == 3)

@lms
def testWhile(x):
  z = 0
  while z < x:
    z = z + 1
  return z

print("======= Original code =======")
print(testWhile.original_src)
print("======= Converted code ========")
print(testWhile.src)
val = testWhile(2)
assert(val == 3)
print("\n")

@stage
def runWhile(x):
  return testWhile(x)

print("======= SExpr ========")
print(runWhile.code)
print("\n")
print("======= C/C++ code ========")
print(runWhile.Ccode)
val = runWhile(10)
assert(val == 10)

@lms
def run(x):
  def power(n, k):
    if k == 0:
      return 1
    else:
      return n * power(n, k - 1)
  res = power(x, 3)
  return res

print("======= Original code =======")
print(run.original_src)
print("======= Converted code ========")
print(run.src)
print("\n")

@stage
def runX(x):
  return run(x)

print("======= SExpr ========")
print(runX.code)
print("\n")
print("======= C/C++ code ========")
print(runX.Ccode)
val = runX(5)
assert(val == 125)

@lms
def testFor(x):
  s = 0
  for i in x:
    s = s + i
  return s

print(testFor.src)

# @stage
# def runFor(x):
#   return testFor(x)

# print(runFor.code)
