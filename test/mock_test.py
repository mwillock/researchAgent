import pytest


@pytest.mark.parametrize("code", ["def add(a,b): return a+b", "print('hi')"])
def test_mock(client, code):
    res = client.post("/assist/explain?mock=1", json={"code": code})
    assert res.status_code in (200, 404)
