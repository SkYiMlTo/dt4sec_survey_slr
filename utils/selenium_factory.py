"""
utils/selenium_factory.py
=========================
Centralised factory for headless Chrome ``webdriver`` instances.

All extractors that require Selenium should call ``build_driver()`` instead
of configuring Chrome options themselves.  This eliminates the copy-paste
options blocks that existed in every old extractor and ensures that any
future hardening (e.g., new anti-detection flags) is applied everywhere.

Anti-detection measures applied
--------------------------------
- ``--disable-blink-features=AutomationControlled`` removes the
  ``navigator.webdriver`` flag that sites check
- ``excludeSwitches`` removes ``enable-automation`` from the Chrome
  info-bar
- A realistic window size is used instead of the default tiny headless one
- ``navigator.webdriver`` is also patched via ``execute_cdp_cmd`` after
  launch (call ``patch_driver(driver)`` for this)
"""
from __future__ import annotations

import logging
import random
from typing import Final

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger(__name__)

# Realistic viewport sizes (width, height)
_VIEWPORTS: Final[list[tuple[int, int]]] = [
    (1920, 1080),
    (1366, 768),
    (1440, 900),
    (1536, 864),
    (1280, 800),
]

# Matching user agents for each viewport (same order)
_USER_AGENTS: Final[list[str]] = [
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0"
    ),
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/121.0.0.0 Safari/537.36"
    ),
]


def build_driver(
    *,
    headless: bool = True,
    chromedriver_path: str | None = None,
    page_load_timeout: int = 60,
    implicit_wait: int = 0,  # prefer explicit waits; keep at 0
) -> webdriver.Chrome:
    """Create and return a configured Chrome ``WebDriver``.

    Parameters
    ----------
    headless:
        Run Chrome in headless mode (default ``True``).
        Set to ``False`` for local debugging.
    chromedriver_path:
        Explicit path to the ``chromedriver`` binary.  When ``None``,
        Selenium 4's auto-detection / ``webdriver-manager`` is used.
    page_load_timeout:
        Seconds before Selenium raises ``TimeoutException`` on page load.
    implicit_wait:
        Implicit element wait in seconds.  Keep at 0 and use
        ``WebDriverWait`` with ``expected_conditions`` instead.
    """
    options = Options()

    # --- Headless mode ---------------------------------------------------
    if headless:
        options.add_argument("--headless=new")  # new headless is more faithful

    # --- Stability flags (required in Docker / CI) ------------------------
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-infobars")

    # --- Anti-detection --------------------------------------------------
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # --- Realistic viewport + UA -----------------------------------------
    idx = random.randrange(len(_VIEWPORTS))
    w, h = _VIEWPORTS[idx]
    ua = _USER_AGENTS[idx]
    options.add_argument(f"--window-size={w},{h}")
    options.add_argument(f"--user-agent={ua}")

    # --- Misc performance ------------------------------------------------
    options.add_argument("--blink-settings=imagesEnabled=false")  # skip images
    options.add_argument("--disable-javascript-harmony-shipping")

    # Build the driver
    if chromedriver_path:
        service = Service(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)
    else:
        driver = webdriver.Chrome(options=options)

    driver.set_page_load_timeout(page_load_timeout)
    if implicit_wait:
        driver.implicitly_wait(implicit_wait)

    # Patch navigator.webdriver via CDP
    patch_driver(driver)

    logger.debug("Chrome WebDriver created (headless=%s, viewport=%dx%d)", headless, w, h)
    return driver


def patch_driver(driver: webdriver.Chrome) -> None:
    """Inject CDP commands to mask automation fingerprints."""
    try:
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined,
                    });
                """
            },
        )
        driver.execute_cdp_cmd(
            "Network.setUserAgentOverride",
            {"userAgent": driver.execute_script("return navigator.userAgent")},
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("CDP patch skipped: %s", exc)


def make_wait(driver: webdriver.Chrome, timeout: int = 30) -> WebDriverWait:
    """Return a ``WebDriverWait`` bound to *driver* with *timeout* seconds."""
    return WebDriverWait(driver, timeout)


def dismiss_cookie_banner(
    driver: webdriver.Chrome,
    *xpaths: str,
    timeout: int = 5,
) -> bool:
    """Try each XPath in turn and click the first element found.

    Returns True if a banner was dismissed, False otherwise.
    Errors are swallowed intentionally — cookie banners are best-effort.
    """
    wait = WebDriverWait(driver, timeout)
    for xpath in xpaths:
        try:
            btn = wait.until(EC.element_to_be_clickable(("xpath", xpath)))
            btn.click()
            logger.debug("Cookie banner dismissed via XPath: %s", xpath)
            return True
        except Exception:  # noqa: BLE001
            continue
    return False
