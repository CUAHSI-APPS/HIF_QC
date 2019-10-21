import pytest

from pylms import lms, lmscompile
from pylms.rep import *

# power doesn't need virtualization
# sanity check that @lms doesn't mess up

def power1(b, x):
    if (x == 0): return 1
    else: return b * power1(b, x-1)

@lms
def power2(b, x):
    if (x == 0): return 1
    else: return b * power2(b, x-1)

def test_power():
    assert(power1(2,3) == 8)
    assert(power2(2,3) == 8)

def test_power_staged():
    assert(lmscompile(lambda x: power1(x,3)).code ==
        "['begin', ['let', x0, ['*', in, 1]], ['let', x1, ['*', in, x0]], ['let', x2, ['*', in, x1]], x2]")
    assert(lmscompile(lambda x: power2(x,3)).code ==
        "['begin', ['let', x0, ['*', in, 1]], ['let', x1, ['*', in, x0]], ['let', x2, ['*', in, x1]], x2]")

def test_power_rewrite():
    assert(power2.src == """

def power2(b, x):
    try:

        def then$1():
            _return(1)

        def else$1():
            _return((b * power2(b, (x - 1))))
        _if((x == 0), then$1, else$1)
    except NonLocalReturnValue as r:
        return r.value
""")


@lms
def foobar1(x):
    if x == 0:
        print('yes')
    else:
        print('no')
    return x


def test_foobar1():
    assert lmscompile(lambda _: foobar1(7)).code == """['begin', 7]"""


def test_foobar1_staged():
    foobar1_code = lmscompile(foobar1).code
    print(foobar1_code)
    assert(foobar1_code ==
"""
['begin', ['let', x0, ['==', in, 0]],
 ['let', x1, ['if', x0,
  ['begin', ['let', x1, ['print', '"yes"']], None],
  ['begin', ['let', x1, ['print', '"no"']], None]]], in]
""".replace('\n','').replace('  ',' ').replace('  ',' '))


def test_foobar1_rewrite():
    assert(foobar1.src == """

def foobar1(x):
    try:

        def then$1():
            _print('yes')

        def else$1():
            _print('no')
        _if((x == 0), then$1, else$1)
        _return(x)
    except NonLocalReturnValue as r:
        return r.value
""")

@lms
def foobar2(x):
    if x == 0:
        return "yes"
    else:
        return "no"

def test_foobar2():
    assert(foobar2(7) == "no")

def test_foobar2_staged():
    assert(lmscompile(foobar2).code ==
        """['begin', ['let', x0, ['==', in, 0]], ['let', x1, ['if', x0, ['begin', 'yes'], ['begin', 'no']]], x1]""")

def test_foobar2_rewrite():
    assert(foobar2.src == """

def foobar2(x):
    try:

        def then$1():
            _return('yes')

        def else$1():
            _return('no')
        _if((x == 0), then$1, else$1)
    except NonLocalReturnValue as r:
        return r.value
""")


@lms
def loop1(n):
    x = 0
    while x < n:
        x = x + 1
    return x

def test_loop1():
    assert(loop1(7) == 7)

def test_loop1_staged():
    assert(lmscompile(loop1).code ==
"""
['begin', ['let', x7, ['new']],
    ['let', x8, ['set', x7, 0]],
    ['let', x9, ['get', x7]],
    ['let', x10, ['<', x9, in]],
    ['let', x11, ['while', ['begin',
        ['let', x11, ['get', x7]],
        ['let', x12, ['<', x11, in]], x12],
        ['begin', ['let', x11, ['get', x7]],
        ['let', x12, ['+', x11, 1]],
        ['let', x13, ['set', x7, x12]],
        None]]],
    ['let', x12, ['get', x7]], x12]
""".replace('\n','').replace('  ',' ').replace('  ',' ').replace('  ',' '))

def test_loop1_rewrite():
    assert(loop1.src == """

def loop1(n):
    try:
        x = _var()
        _assign(x, 0)

        def cond$1():
            return (_read(x) < n)

        def body$1():
            _assign(x, (_read(x) + 1))
        _while(cond$1, body$1)
        _return(_read(x))
    except NonLocalReturnValue as r:
        return r.value
""")

