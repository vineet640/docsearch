FIXTURE = "tests/fixtures/test_doc.pdf"

def upload(client, name, path):
    with open(path, "rb") as f:
        return client.post("/upload", files = [("files", (name, f, "application/pdf"))])

def test_upload_then_search(client):
    r = upload(client, "test_doc.pdf", FIXTURE)
    assert r.status_code == 200
    results = client.get("/search", params = {"q": "quokka rooftop garden"}).json()
    assert results[0]["document"] == "test_doc.pdf"

def test_upload_txt_returns_400(client):
    r = client.post("/upload", files = [("files", ("notes.txt", b"hello", "text/plain"))])
    assert r.status_code == 400

def test_short_query_returns_422(client):
    r = client.get("/search", params = {"q": "a"})
    assert r.status_code == 422

def test_documents_lists_upload(client):
    upload(client, "test_doc.pdf", FIXTURE)
    names = [d["name"] for d in client.get("/documents").json()]
    assert "test_doc.pdf" in names