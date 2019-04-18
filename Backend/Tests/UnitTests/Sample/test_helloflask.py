import pytest
from helloflask import app

@pytest.fixture(scope='module')
def client():
    testing_client = app.test_client()
    yield testing_client

# no mocks needed
def test_example(client):
    response = client.get('/')
    assert(response.status_code == 200)