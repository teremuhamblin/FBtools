import pytest


class FakeResponse:
    def __init__(self, payload, status=200):
        self._payload, self.status_code = payload, status
        self.ok = status < 400
        self.text = str(payload)

    def json(self):
        return self._payload


class FakeSession:
    """Session HTTP factice : associe (méthode, fragment d'URL) -> liste de réponses."""

    def __init__(self, routes):
        self.routes, self.calls, self.headers = routes, [], {}

    def request(self, method, url, params=None, data=None, timeout=None):
        self.calls.append((method, url, dict(params or {}), dict(data or {})))
        for (m, frag), responses in self.routes.items():
            if m == method and frag in url:
                r = responses.pop(0) if len(responses) > 1 else responses[0]
                return r if isinstance(r, FakeResponse) else FakeResponse(r)
        raise AssertionError(f"Route inattendue : {method} {url}")


@pytest.fixture
def fake():
    return FakeSession, FakeResponse


@pytest.fixture(autouse=True)
def isolated_config(tmp_path, monkeypatch):
    monkeypatch.setenv("FBTOOLS_CONFIG_DIR", str(tmp_path))
    for var in ("FBTOOLS_ACCESS_TOKEN", "FBTOOLS_APP_SECRET", "FBTOOLS_API_VERSION"):
        monkeypatch.delenv(var, raising=False)
