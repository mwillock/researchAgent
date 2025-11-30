from fastapi.testclient import TestClient
from app.main import create_app


def get_client():
    app = create_app()
    return TestClient(app)


def test_explain_mock():
    client = get_client()
    resp = client.post(
        "/assist/explain?mock=1",
        json={"code": "def add(a, b): return a + b"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True
    assert body["task"] == "explain"
    assert "summary" in body["result"]


def test_review_diff_mock():
    client = get_client()
    diff = """\
        diff --git a/example.py b/example.py
        --- a/example.py
        +++ b/example.py
        @@ -1,3 +1,4 @@
        -def add(a, b):
        -    return a + b
        +def add(a, b):
        +    #TODO: Handle non-numeric inputs
        +    return a + b
        """
    resp = client.post(
        "/assist/review-diff?mock=1",
        json={"diff": diff, "context": "simple math helper"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True
    assert body["task"] == "review-diff"
    assert "summary" in body["result"]


def test_mock():
    client = get_client()
    resp = client.post(
        "/assist/test?mock=1",
        json={
            "code": "def add(a, b): return a + b",
            "spec": "add should sum two numbers",
            "framework": "pytest",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True
    assert body["task"] == "tests"
    assert "summary" in body["result"]
