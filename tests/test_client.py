import pytest

from fbtools.client import GraphAPIError, GraphClient


def make(fake, routes, **kw):
    FakeSession, _ = fake
    s = FakeSession(routes)
    return GraphClient("USERTOKEN", session=s, **kw), s


def test_pagination_follows_next(fake):
    client, s = make(
        fake,
        {
            ("GET", "/v27.0/me/accounts"): [
                {
                    "data": [{"id": "1", "access_token": "P1"}],
                    "paging": {"next": "https://graph.facebook.com/next"},
                }
            ],
            ("GET", "/next"): [{"data": [{"id": "2", "access_token": "P2"}]}],
        },
    )
    pages = client.pages()
    assert [p["id"] for p in pages] == ["1", "2"]
    assert client.page_token("2") == "P2"  # mis en cache, pas de requête supplémentaire
    assert len(s.calls) == 2


def test_publish_scheduled_uses_page_token(fake):
    client, s = make(
        fake,
        {
            ("GET", "/v27.0/123"): [{"access_token": "PAGETOKEN", "id": "123"}],
            ("POST", "/v27.0/123/feed"): [{"id": "123_456"}],
        },
    )
    res = client.publish("123", message="Bonjour", scheduled_unix=1900000000)
    assert res["id"] == "123_456"
    _, _, params, data = s.calls[-1]
    assert params["access_token"] == "PAGETOKEN"
    assert data == {
        "message": "Bonjour",
        "published": "false",
        "scheduled_publish_time": "1900000000",
    }


def test_appsecret_proof(fake):
    client, s = make(fake, {("GET", "/me"): [{"id": "1", "name": "A"}]}, app_secret="secret")
    client.me()
    assert len(s.calls[0][2]["appsecret_proof"]) == 64


def test_error_raises(fake):
    _, FakeResponse = fake
    client, _ = make(
        fake,
        {
            ("GET", "/me"): [
                FakeResponse(
                    {
                        "error": {
                            "message": "Invalid OAuth access token",
                            "code": 190,
                            "fbtrace_id": "X",
                        }
                    },
                    400,
                )
            ]
        },
    )
    with pytest.raises(GraphAPIError) as exc:
        client.me()
    assert exc.value.code == 190
    assert "190" in str(exc.value)


def test_retry_on_rate_limit(fake, monkeypatch):
    _, FakeResponse = fake
    monkeypatch.setattr("fbtools.client.time.sleep", lambda s: None)
    client, s = make(
        fake,
        {
            ("GET", "/me"): [
                FakeResponse({"error": {"message": "limit", "code": 4}}, 400),
                {"id": "1", "name": "A"},
            ]
        },
    )
    assert client.me()["id"] == "1"
    assert len(s.calls) == 2


def test_publish_requires_content(fake):
    client, _ = make(fake, {})
    with pytest.raises(ValueError, match="--message"):
        client.publish("123")


def test_retry_on_network_error(fake, monkeypatch):
    import requests

    monkeypatch.setattr("fbtools.client.time.sleep", lambda s: None)
    FakeSession, _ = fake

    class Flaky(FakeSession):
        failures = 1

        def request(self, *a, **kw):
            if self.failures:
                self.failures -= 1
                raise requests.ConnectionError("coupure")
            return super().request(*a, **kw)

    client = GraphClient("T", session=Flaky({("GET", "/me"): [{"id": "1", "name": "A"}]}))
    assert client.me()["id"] == "1"


def test_network_error_after_retries(fake, monkeypatch):
    import requests

    monkeypatch.setattr("fbtools.client.time.sleep", lambda s: None)
    FakeSession, _ = fake

    class Down(FakeSession):
        def request(self, *a, **kw):
            raise requests.Timeout("délai dépassé")

    client = GraphClient("T", session=Down({}), max_retries=2)
    with pytest.raises(GraphAPIError, match="réseau"):
        client.me()


def test_server_error_is_retried_then_raised(fake, monkeypatch):
    _, FakeResponse = fake
    monkeypatch.setattr("fbtools.client.time.sleep", lambda s: None)
    client, s = make(fake, {("GET", "/me"): [FakeResponse("boom", 503)]}, max_retries=1)
    with pytest.raises(GraphAPIError):
        client.me()
    assert len(s.calls) == 2


def test_non_json_response(fake):
    _, FakeResponse = fake

    class Raw(FakeResponse):
        def json(self):
            raise ValueError

    client, _ = make(fake, {("GET", "/me"): [Raw("Bad Gateway", 400)]})
    with pytest.raises(GraphAPIError, match="Bad Gateway"):
        client.me()


def test_backoff_delay_is_capped():
    from fbtools.client import backoff_delay

    assert [backoff_delay(i) for i in range(4)] == [1, 2, 4, 8]
    assert backoff_delay(10) == 30


def test_missing_token_rejected():
    with pytest.raises(ValueError, match="set-token"):
        GraphClient("")


def test_page_token_missing(fake):
    client, _ = make(fake, {("GET", "/v27.0/123"): [{"id": "123"}]})
    with pytest.raises(GraphAPIError, match="jeton de la Page"):
        client.page_token("123")


def test_pagination_respects_limit(fake):
    client, s = make(
        fake,
        {
            ("GET", "/v27.0/1/posts"): [
                {
                    "data": [{"id": "a"}, {"id": "b"}, {"id": "c"}],
                    "paging": {"next": "https://graph.facebook.com/n"},
                }
            ],
            ("GET", "/v27.0/1"): [{"access_token": "P"}],
        },
    )
    assert [p["id"] for p in client.posts("1", limit=2)] == ["a", "b"]
    assert s.calls[-1][2]["limit"] == 2


def test_delete_comments_insights(fake):
    client, s = make(
        fake,
        {
            ("GET", "/v27.0/1/comments"): [{"data": [{"id": "c1"}]}],
            ("GET", "/v27.0/1/insights"): [{"data": [{"name": "page_follows"}]}],
            ("DELETE", "/v27.0/1_2"): [{"success": True}],
            ("GET", "/v27.0/1"): [{"access_token": "P"}],
        },
    )
    assert client.delete_post("1_2") == {"success": True}
    assert client.comments(["1", "2"][0]) == [{"id": "c1"}]
    data = client.insights("1", ["page_follows"], since="2026-11-01", until="2026-11-02")
    assert data[0]["name"] == "page_follows"
    assert s.calls[-1][2]["since"] == "2026-11-01"


def test_error_str_with_subcode():
    err = GraphAPIError("Oups", code=100, subcode=33, fbtrace_id="T")
    assert str(err) == "Oups (code 100, sous-code 33) [fbtrace_id T]"
