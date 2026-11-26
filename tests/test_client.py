import pytest

from fbtools.client import GraphAPIError, GraphClient


def make(fake, routes, **kw):
    FakeSession, _ = fake
    s = FakeSession(routes)
    return GraphClient("USERTOKEN", session=s, **kw), s


def test_pagination_follows_next(fake):
    client, s = make(fake, {
        ("GET", "/v27.0/me/accounts"): [{"data": [{"id": "1", "access_token": "P1"}],
                                         "paging": {"next": "https://graph.facebook.com/next"}}],
        ("GET", "/next"): [{"data": [{"id": "2", "access_token": "P2"}]}],
    })
    pages = client.pages()
    assert [p["id"] for p in pages] == ["1", "2"]
    assert client.page_token("2") == "P2"  # mis en cache, pas de requête supplémentaire
    assert len(s.calls) == 2


def test_publish_scheduled_uses_page_token(fake):
    client, s = make(fake, {
        ("GET", "/v27.0/123"): [{"access_token": "PAGETOKEN", "id": "123"}],
        ("POST", "/v27.0/123/feed"): [{"id": "123_456"}],
    })
    res = client.publish("123", message="Bonjour", scheduled_unix=1900000000)
    assert res["id"] == "123_456"
    _, _, params, data = s.calls[-1]
    assert params["access_token"] == "PAGETOKEN"
    assert data == {"message": "Bonjour", "published": "false",
                    "scheduled_publish_time": "1900000000"}


def test_appsecret_proof(fake):
    client, s = make(fake, {("GET", "/me"): [{"id": "1", "name": "A"}]}, app_secret="secret")
    client.me()
    assert len(s.calls[0][2]["appsecret_proof"]) == 64


def test_error_raises(fake):
    _, FakeResponse = fake
    client, _ = make(fake, {("GET", "/me"): [FakeResponse(
        {"error": {"message": "Invalid OAuth access token", "code": 190, "fbtrace_id": "X"}}, 400)]})
    with pytest.raises(GraphAPIError) as exc:
        client.me()
    assert exc.value.code == 190 and "190" in str(exc.value)


def test_retry_on_rate_limit(fake, monkeypatch):
    _, FakeResponse = fake
    monkeypatch.setattr("fbtools.client.time.sleep", lambda s: None)
    client, s = make(fake, {("GET", "/me"): [
        FakeResponse({"error": {"message": "limit", "code": 4}}, 400),
        {"id": "1", "name": "A"},
    ]})
    assert client.me()["id"] == "1"
    assert len(s.calls) == 2


def test_publish_requires_content(fake):
    client, _ = make(fake, {})
    with pytest.raises(ValueError):
        client.publish("123")
