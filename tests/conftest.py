import os
os.environ["BLOB_CONTAINER"] = "documents-test"

import pytest
from fastapi.testclient import TestClient
from app import storage
from app.main import app

@pytest.fixture(scope = "session")
def client():
    container = storage._container()
    for blob in container.list_blobs():
        container.delete_blob(blob.name)
    with TestClient(app) as c:
        yield c