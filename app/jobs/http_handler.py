"""HTTP fetch job handler with basic SSRF checks."""

from __future__ import annotations

import ipaddress
import socket
from typing import Any
from urllib.parse import urlparse

import httpx


def handle_http_fetch(payload: dict[str, Any]) -> dict[str, Any]:
    """GET payload['url'] after rejecting private/loopback targets."""
    url = payload.get("url")
    if not url or not isinstance(url, str):
        raise ValueError("url is required")
    assert_safe_url(url)
    with httpx.Client(timeout=15.0, follow_redirects=False) as client:
        response = client.get(url)
    return {
        "url": url,
        "status_code": response.status_code,
        "body_length": len(response.content),
    }


def assert_safe_url(url: str) -> None:
    """Reject non-http(s) schemes and hosts that resolve to private space."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("url scheme must be http or https")
    host = parsed.hostname
    if not host:
        raise ValueError("url host is required")
    if host.lower() in {"localhost", "metadata.google.internal"}:
        raise ValueError("url host is not allowed")
    _reject_blocked_ips(host)


def _reject_blocked_ips(host: str) -> None:
    """Resolve host and raise if any address is private or reserved."""
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror as exc:
        raise ValueError(f"could not resolve host: {host}") from exc
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            raise ValueError(f"url resolves to blocked address: {ip}")
