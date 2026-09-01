"""Rate limiting.

A small abstraction with an in-process fixed-window implementation — enough for a
single instance and for tests. For a multi-instance deployment, add a
``RedisRateLimiter`` implementing the same interface and select it here; nothing
else in the app changes.
"""

from __future__ import annotations

import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.core.config import settings


@dataclass(frozen=True)
class RateLimitResult:
    allowed: bool
    retry_after: int  # seconds until the window resets (0 when allowed)


class RateLimiter(ABC):
    @abstractmethod
    def check(self, key: str, *, limit: int, window_seconds: int) -> RateLimitResult:
        """Register a hit for ``key`` and report whether it is within ``limit``."""


class InMemoryRateLimiter(RateLimiter):
    def __init__(self) -> None:
        self._hits: dict[str, list[float]] = {}
        self._lock = threading.Lock()

    def check(self, key: str, *, limit: int, window_seconds: int) -> RateLimitResult:
        now = time.monotonic()
        cutoff = now - window_seconds
        with self._lock:
            bucket = [t for t in self._hits.get(key, []) if t > cutoff]
            if len(bucket) >= limit:
                retry_after = int(bucket[0] + window_seconds - now) + 1
                self._hits[key] = bucket
                return RateLimitResult(allowed=False, retry_after=max(retry_after, 1))
            bucket.append(now)
            self._hits[key] = bucket
            return RateLimitResult(allowed=True, retry_after=0)

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


class NullRateLimiter(RateLimiter):
    def check(self, key: str, *, limit: int, window_seconds: int) -> RateLimitResult:
        return RateLimitResult(allowed=True, retry_after=0)


_limiter: RateLimiter | None = None


def get_rate_limiter() -> RateLimiter:
    global _limiter
    if _limiter is None:
        _limiter = InMemoryRateLimiter() if settings.rate_limit_enabled else NullRateLimiter()
    return _limiter


def reset_rate_limiter() -> None:
    """Test hook."""
    global _limiter
    _limiter = None
