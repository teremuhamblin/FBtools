"""Client minimal et robuste pour l'API Graph de Meta."""

from __future__ import annotations

import hashlib
import hmac
import time
from collections.abc import Iterator
from typing import Any

import requests

from . import DEFAULT_API_VERSION, __version__

GRAPH_URL = "https://graph.facebook.com"
RETRYABLE_CODES = {1, 2, 4, 17, 32, 341, 613}  # erreurs temporaires / limites de débit


def backoff_delay(attempt: int, cap: float = 30.0) -> float:
    """Délai exponentiel avant la tentative suivante : 1 s, 2 s, 4 s… plafonné à ``cap``."""
    return float(min(2**attempt, cap))


class GraphAPIError(Exception):
    """Erreur renvoyée par l'API Graph (ou erreur réseau définitive)."""

    def __init__(
        self,
        message: str,
        code: int | None = None,
        subcode: int | None = None,
        fbtrace_id: str | None = None,
        status: int | None = None,
    ):
        super().__init__(message)
        self.message, self.code, self.subcode = message, code, subcode
        self.fbtrace_id, self.status = fbtrace_id, status

    def __str__(self) -> str:
        parts = [self.message]
        if self.code is not None:
            parts.append(
                f"(code {self.code}" + (f", sous-code {self.subcode})" if self.subcode else ")")
            )
        if self.fbtrace_id:
            parts.append(f"[fbtrace_id {self.fbtrace_id}]")
        return " ".join(parts)


class GraphClient:
    """Client HTTP de l'API Graph : authentification, pagination, retries, jetons de Page."""

    def __init__(
        self,
        access_token: str,
        api_version: str = DEFAULT_API_VERSION,
        app_secret: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        session: requests.Session | None = None,
    ):
        if not access_token:
            raise ValueError("Jeton d'accès manquant. Lancez `fbtools config set-token`.")
        self.access_token = access_token
        self.api_version = api_version
        self.app_secret = app_secret
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = session or requests.Session()
        self.session.headers.setdefault("User-Agent", f"fbtools/{__version__}")
        self._page_tokens: dict[str, str] = {}

    # ---------- bas niveau ----------
    def _auth_params(self, token: str) -> dict[str, str]:
        params = {"access_token": token}
        if self.app_secret:
            params["appsecret_proof"] = hmac.new(
                self.app_secret.encode(), token.encode(), hashlib.sha256
            ).hexdigest()
        return params

    def request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        token: str | None = None,
    ) -> dict[str, Any]:
        url = (
            path
            if path.startswith("http")
            else f"{GRAPH_URL}/{self.api_version}/{path.lstrip('/')}"
        )
        query = dict(params or {})
        if not path.startswith("http"):
            query.update(self._auth_params(token or self.access_token))
        for attempt in range(self.max_retries + 1):
            try:
                resp = self.session.request(
                    method, url, params=query, data=data, timeout=self.timeout
                )
            except (requests.ConnectionError, requests.Timeout) as exc:
                if attempt < self.max_retries:
                    time.sleep(backoff_delay(attempt))
                    continue
                raise GraphAPIError(f"Erreur réseau : {exc}") from exc
            payload: Any
            try:
                payload = resp.json()
            except ValueError:
                payload = {"error": {"message": resp.text or f"HTTP {resp.status_code}"}}
            err = payload.get("error") if isinstance(payload, dict) else None
            if not err and resp.ok:
                result: dict[str, Any] = payload if isinstance(payload, dict) else {"data": payload}
                return result
            err = err or {"message": f"HTTP {resp.status_code}"}
            code = err.get("code")
            if (code in RETRYABLE_CODES or resp.status_code >= 500) and attempt < self.max_retries:
                time.sleep(backoff_delay(attempt))
                continue
            raise GraphAPIError(
                err.get("message", "Erreur inconnue"),
                code,
                err.get("error_subcode"),
                err.get("fbtrace_id"),
                resp.status_code,
            )
        raise GraphAPIError("Nombre maximal de tentatives atteint")  # pragma: no cover

    def get(self, path: str, **params: Any) -> dict[str, Any]:
        return self.request("GET", path, params=params)

    def paginate(
        self, path: str, limit: int | None = None, token: str | None = None, **params: Any
    ) -> Iterator[dict[str, Any]]:
        """Itère sur tous les éléments d'une arête paginée (suit paging.next)."""
        if limit:
            params.setdefault("limit", min(limit, 100))
        page = self.request("GET", path, params=params, token=token)
        count = 0
        while True:
            for item in page.get("data", []):
                yield item
                count += 1
                if limit and count >= limit:
                    return
            nxt = page.get("paging", {}).get("next")
            if not nxt:
                return
            page = self.request("GET", nxt)

    # ---------- haut niveau ----------
    def me(self) -> dict[str, Any]:
        return self.get("me", fields="id,name")

    def permissions(self) -> list[dict[str, Any]]:
        return list(self.paginate("me/permissions"))

    def pages(self) -> list[dict[str, Any]]:
        pages = list(self.paginate("me/accounts", fields="id,name,category,access_token,tasks"))
        for p in pages:
            if p.get("access_token"):
                self._page_tokens[p["id"]] = p["access_token"]
        return pages

    def page_token(self, page_id: str) -> str:
        """Récupère (et met en cache) le jeton de Page nécessaire aux écritures."""
        if page_id not in self._page_tokens:
            data = self.get(page_id, fields="access_token")
            token = data.get("access_token")
            if not token:
                raise GraphAPIError(
                    f"Impossible d'obtenir le jeton de la Page {page_id}. "
                    "Vérifiez que vous l'administrez et les permissions pages_manage_posts."
                )
            self._page_tokens[page_id] = token
        return self._page_tokens[page_id]

    def posts(self, page_id: str, limit: int = 25) -> list[dict[str, Any]]:
        fields = "id,message,created_time,permalink_url,status_type"
        return list(
            self.paginate(
                f"{page_id}/posts", limit=limit, fields=fields, token=self.page_token(page_id)
            )
        )

    def publish(
        self,
        page_id: str,
        message: str | None = None,
        link: str | None = None,
        scheduled_unix: int | None = None,
    ) -> dict[str, Any]:
        if not message and not link:
            raise ValueError("Indiquez au moins --message ou --link.")
        data: dict[str, Any] = {}
        if message:
            data["message"] = message
        if link:
            data["link"] = link
        if scheduled_unix:
            data["published"] = "false"
            data["scheduled_publish_time"] = str(scheduled_unix)
        return self.request("POST", f"{page_id}/feed", data=data, token=self.page_token(page_id))

    def delete_post(self, post_id: str) -> dict[str, Any]:
        page_id = post_id.split("_", 1)[0]
        return self.request("DELETE", post_id, token=self.page_token(page_id))

    def comments(self, object_id: str, limit: int | None = None) -> list[dict[str, Any]]:
        page_id = object_id.split("_", 1)[0]
        fields = "id,from{id,name},message,created_time,like_count,comment_count"
        return list(
            self.paginate(
                f"{object_id}/comments",
                limit=limit,
                fields=fields,
                filter="stream",
                order="chronological",
                token=self.page_token(page_id),
            )
        )

    def insights(
        self,
        page_id: str,
        metrics: list[str],
        period: str = "day",
        since: str | None = None,
        until: str | None = None,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {"metric": ",".join(metrics), "period": period}
        if since:
            params["since"] = since
        if until:
            params["until"] = until
        res = self.request(
            "GET", f"{page_id}/insights", params=params, token=self.page_token(page_id)
        )
        data: list[dict[str, Any]] = res.get("data", [])
        return data
