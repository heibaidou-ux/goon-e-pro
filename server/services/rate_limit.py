"""轻量级速率限制 — 内存实现，无外部依赖"""
import time
from collections import defaultdict
from typing import Optional
from fastapi import Request, HTTPException, status


class MemoryRateLimiter:
    """Simple in-memory sliding window rate limiter."""

    def __init__(self):
        # key -> [(timestamp, count), ...]
        self._windows: dict[str, list] = defaultdict(list)

    def check(self, key: str, max_requests: int, window_seconds: int = 60) -> bool:
        """Check if request exceeds rate limit. Returns True if allowed."""
        now = time.time()
        # Clean old entries
        self._windows[key] = [
            ts for ts in self._windows[key]
            if now - ts < window_seconds
        ]
        if len(self._windows[key]) >= max_requests:
            return False
        self._windows[key].append(now)
        return True


# 全局唯一实例
limiter = MemoryRateLimiter()


def rate_limit(max_requests: int = 60, window_seconds: int = 60):
    """Decorator-like dependency for rate limiting.
    Usage: rate_limit(5, 60) on login endpoints.
    """
    def dependency(request: Request):
        client_ip = request.client.host if request.client else "unknown"
        if not limiter.check(f"{request.url.path}:{client_ip}", max_requests, window_seconds):
            raise HTTPException(
                status_code=429,
                detail=f"请求过于频繁，请{window_seconds}秒后再试"
            )
        return True
    return dependency
