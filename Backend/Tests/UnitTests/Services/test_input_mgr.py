import pytest
import redis
import fakeredis

# redis is invoked on start
redis.Redis = fakeredis.FakeRedis

from Backend.Services.Input_Mgr.input_mgr import app

@pytest.fixture(scope='module')
def client():
    redis.StrictRedis = fakeredis.FakeStrictRedis
    testing_client = app.test_client()
    yield testing_client

def test_GettingCsvFileSuccessfully(client):
    response = client.get('/') 
    response.status_code == 200
    response.data == "Hello world"