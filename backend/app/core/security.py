import hashlib
import hmac
import os
import secrets
import time
from collections import defaultdict
from threading import Lock

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from backend.app.core.config import settings


class SecurityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self._sessions = set()
        self._session_lock = Lock()
        self._rate_windows = defaultdict(lambda: [0.0, 0])
        self._rate_lock = Lock()

    def _session_token(self) -> str:
        return hmac.new(
            settings.API_KEY.encode(), b"fantasy-dominator-browser", hashlib.sha256
        ).hexdigest()

    def _auth_required(self) -> bool:
        return bool(settings.API_KEY)

    def _is_authenticated(self, request: Request) -> bool:
        supplied_key = request.headers.get("X-API-Key", "")
        cookie = request.cookies.get("fd_session", "")
        return (
            bool(settings.API_KEY)
            and hmac.compare_digest(supplied_key, settings.API_KEY)
        ) or (
            bool(settings.API_KEY)
            and hmac.compare_digest(cookie, self._session_token())
        )

    def _rate_limited(self, request: Request) -> bool:
        client = request.client.host if request.client else "unknown"
        now = time.monotonic()
        with self._rate_lock:
            window_start, count = self._rate_windows[client]
            if now - window_start >= 60:
                window_start, count = now, 0
            count += 1
            self._rate_windows[client] = [window_start, count]
            return count > settings.RATE_LIMIT_PER_MINUTE

    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/api/v1/health":
            return await call_next(request)

        if self._auth_required() and not self._is_authenticated(request):
            if request.method == "GET" and request.url.path == "/":
                response = await call_next(request)
                response.set_cookie(
                    "fd_session",
                    self._session_token(),
                    httponly=True,
                    samesite="lax",
                    secure=request.url.scheme == "https",
                    max_age=3600,
                )
                return response
            return JSONResponse({"detail": "Authentication required"}, status_code=401)

        if request.url.path.startswith("/api/") and self._rate_limited(request):
            return JSONResponse({"detail": "Rate limit exceeded"}, status_code=429)

        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; style-src 'self' https://fonts.googleapis.com 'unsafe-inline'; "
            "font-src 'self' https://fonts.gstatic.com; script-src 'self'; img-src 'self' data:;",
        )
        return response