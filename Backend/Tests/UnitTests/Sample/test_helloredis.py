from helloredis import *
try:
    from mock import MagicMock
except ImportError:
    from unittest.mock import MagicMock
import pytest
import mock
import redis
import fakeredis

def setup_function():
    redis.StrictRedis = fakeredis.FakeStrictRedis

def test_foo():    
    assert(foo('a') == 'a')