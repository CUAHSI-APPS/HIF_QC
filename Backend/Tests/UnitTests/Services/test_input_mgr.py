import pytest
import redis
import fakeredis
import io
import mock
from mock import mock_open
import json
m = mock_open()
# redis is invoked on start
redis.Redis = fakeredis.FakeRedis

from Backend.Services.Input_Mgr.input_mgr import app, improperFileRequest

@pytest.fixture(scope='module')
def client():
    redis.StrictRedis = fakeredis.FakeStrictRedis
    testing_client = app.test_client()
    yield testing_client

def test_GettingBasePage(client):
    response = client.get('/') 
    response.status_code == 200
    response.data == "Hello world"

# mocking open http://omiron.ro/post/python/how_to_mock_open_file/
# for ref https://stackoverflow.com/questions/35684436/testing-file-uploads-in-flask
def test_UploadingFileSuccessfully(client):

    data = dict(
        file=(io.BytesIO(b'my file contents'), "myfile.csv"),
    )
    with mock.patch('Backend.Services.Input_Mgr.input_mgr.open'):
        response = client.post('/upload/', data=data, content_type='multipart/form-data')
        print (json.loads(response.data)[u'status'])
        assert json.loads(response.data)[u'status'] == "Success" 

def test_UploadingNoFile(client):
    data = dict(
        file=(io.BytesIO(b'my file contents'), ""),
    )
    response = client.post('/upload/', data=data, content_type='multipart/form-data')
    assert response.data == improperFileRequest 
