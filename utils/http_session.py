"""
utils/http_session.py
=====================
Provides a pre-configured ``requests.Session`` with:

- Rotating ``User-Agent`` headers to avoid simple bot detection
- Exponential back-off retry logic (429, 503, 5xx)
- Per-domain rate limiting (token-bucket style)
- Connection + read timeouts

Usage
-----
    from utils.http_session import build_session, RateLimiter

    session = build_session()
    limiter = RateLimiter(calls_per_second=0.5)  # 1 req every 2 s
    limiter.wait()
    response = session.get(url, timeout=(10, 30))
"""
from __future__ import annotations

import logging
import random
import threading
import time
from typing import Final

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# User-Agent pool  (recent real-world UA strings)
# ---------------------------------------------------------------------------

_USER_AGENTS: Final[list[str]] = [
    # Chrome 124 / Windows
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    # Chrome 123 / macOS
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.6312.122 Safari/537.36"
    ),
    # Firefox 125 / Linux
    (
        "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) "
        "Gecko/20100101 Firefox/125.0"
    ),
    # Edge 124 / Windows
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0"
    ),
    # Safari 17 / macOS
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/17.4.1 Safari/605.1.15"
    ),
]

# ---------------------------------------------------------------------------
# Default HTTP headers mimicking a real browser
# ---------------------------------------------------------------------------

_BASE_HEADERS: Final[dict[str, str]] = {
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
}


# ---------------------------------------------------------------------------
# Session builder
# ---------------------------------------------------------------------------


def build_session(
    *,
    max_retries: int = 5,
    backoff_factor: float = 1.5,
    status_forcelist: tuple[int, ...] = (429, 500, 502, 503, 504),
    pool_connections: int = 4,
    pool_maxsize: int = 8,
) -> requests.Session:
    """Return a ``requests.Session`` hardened for long-running scraping.

    Parameters
    ----------
    max_retries:
        Maximum number of retry attempts per request.
    backoff_factor:
        Multiplier for exponential back-off between retries.
        Delay = ``backoff_factor * (2 ** (retry_number - 1))`` seconds.
    status_forcelist:
        HTTP status codes that trigger an automatic retry.
    pool_connections / pool_maxsize:
        Size of the underlying urllib3 connection pool.
    """
    session = requests.Session()

    retry_strategy = Retry(
        total=max_retries,
        backoff_factor=backoff_factor,
        status_forcelist=list(status_forcelist),
        allowed_methods=["HEAD", "GET", "POST", "OPTIONS"],
        raise_on_status=False,
        respect_retry_after_header=True,
    )

    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=pool_connections,
        pool_maxsize=pool_maxsize,
    )
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    # Randomise UA on construction (can be refreshed per-request)
    session.headers.update(_BASE_HEADERS)
    session.headers["User-Agent"] = random.choice(_USER_AGENTS)

    return session


def refresh_user_agent(session: requests.Session) -> None:
    """Pick a new random ``User-Agent`` for *session*."""
    session.headers["User-Agent"] = random.choice(_USER_AGENTS)


# ---------------------------------------------------------------------------
# Rate limiter (token-bucket)
# ---------------------------------------------------------------------------


class RateLimiter:
    """Thread-safe token-bucket rate limiter.

    Parameters
    ----------
    calls_per_second:
        Maximum sustained request rate.  Values < 1 mean "slower than 1/s".
        E.g. ``0.33`` → one request every ~3 seconds.
    min_delay:
        Minimum seconds to wait between calls (regardless of rate).
    jitter:
        If True, add a random ±25 % jitter to each sleep interval to reduce
        the chance of pattern detection by anti-bot systems.
    """

    def __init__(
        self,
        calls_per_second: float = 0.5,
        min_delay: float = 0.5,
        jitter: bool = True,
    ) -> None:
        self._interval = 1.0 / max(calls_per_second, 1e-6)
        self._min_delay = min_delay
        self._jitter = jitter
        self._last_call: float = 0.0
        self._lock = threading.Lock()

    def wait(self) -> None:
        """Block the calling thread until the rate limit allows the next call."""
        with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_call
            sleep_for = max(self._interval - elapsed, self._min_delay)
            if self._jitter:
                sleep_for *= random.uniform(0.75, 1.25)
            if sleep_for > 0:
                logger.debug("Rate limiter sleeping %.2f s", sleep_for)
                time.sleep(sleep_for)
            self._last_call = time.monotonic()
