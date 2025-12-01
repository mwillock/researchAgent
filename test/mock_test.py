import pytest


@pytest.mark.parametrize("code", ["def add(a,b): return a+b", "print('hi')"])
def test_mock(client, code):
    resp = client.post(
        "/assist/explain?mock=1",
        json={"code": code},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True
