"""Browser, login, and Allure evidence."""

from __future__ import annotations

import os
import re
import time
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import allure
import pytest
from dotenv import load_dotenv
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page

from constants import messages
from pages.support_app import SupportApp

load_dotenv(Path(__file__).resolve().parent / ".env")

DEFAULT_APP_URL = "https://bsv-nhungnguyen.github.io/bai_tap_17082026.html"
SCREENSHOT_DIR = Path("screenshots")
VIDEO_DIR = Path("videos")
RAW_VIDEO_DIR = VIDEO_DIR / "raw"


@dataclass(frozen=True)
class Credentials:
    """Account names and passwords loaded from the environment."""

    admin_id: str
    admin_password: str
    guest_id: str
    guest_password: str


def _required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise pytest.UsageError(f"{name} is not set in the environment or .env")
    return value


def _safe_name(nodeid: str) -> str:
    name = nodeid.split("::")[-1]
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", name)[:80]


def _stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")


def _wait_until_video_ready(path: Path) -> bool:
    """Wait until the webm is non-empty and its size has stopped changing."""
    deadline = time.monotonic() + 10
    previous = -1
    stable_reads = 0
    while time.monotonic() < deadline:
        if path.exists():
            size = path.stat().st_size
            if size > 0 and size == previous:
                stable_reads += 1
                if stable_reads >= 2:
                    return True
            else:
                stable_reads = 0
            previous = size
        time.sleep(0.2)
    return path.exists() and path.stat().st_size > 0


def _save_screenshot(item: pytest.Item, page: Page, outcome: str) -> None:
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    path = SCREENSHOT_DIR / f"{_safe_name(item.nodeid)}_{outcome}_{_stamp()}.png"
    try:
        page.screenshot(path=str(path), full_page=True)
    except PlaywrightError:
        return
    if path.stat().st_size <= 0:
        path.unlink(missing_ok=True)
        return
    allure.attach.file(
        str(path),
        name=path.name,
        attachment_type=allure.attachment_type.PNG,
    )


def _finalize_video(item: pytest.Item, failed: bool) -> None:
    raw = getattr(item, "_video_path", None)
    if not raw:
        return
    path = Path(raw)
    ready = _wait_until_video_ready(path)
    if not failed or not ready:
        path.unlink(missing_ok=True)
        return
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    target = VIDEO_DIR / f"{_safe_name(item.nodeid)}_failed_{_stamp()}.webm"
    target.write_bytes(path.read_bytes())
    path.unlink(missing_ok=True)
    if target.stat().st_size <= 0:
        target.unlink(missing_ok=True)
        return
    allure.attach.file(
        str(target),
        name=target.name,
        attachment_type=allure.attachment_type.WEBM,
    )


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args: dict) -> dict:
    headed = os.getenv("HEADED", "false").lower() == "true"
    return {**browser_type_launch_args, "headless": not headed}


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    RAW_VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    return {
        **browser_context_args,
        "viewport": {"width": 1440, "height": 900},
        "record_video_dir": str(RAW_VIDEO_DIR),
        "record_video_size": {"width": 1440, "height": 900},
    }


@pytest.fixture(scope="session")
def app_url() -> str:
    return os.getenv("APP_URL", DEFAULT_APP_URL).strip() or DEFAULT_APP_URL


@pytest.fixture(scope="session")
def credentials() -> Credentials:
    return Credentials(
        admin_id=_required("ADMIN_ID"),
        admin_password=_required("ADMIN_PASSWORD"),
        guest_id=_required("GUEST_ID"),
        guest_password=_required("GUEST_PASSWORD"),
    )


@pytest.fixture(autouse=True)
def _evidence(page: Page, request: pytest.FixtureRequest) -> Iterator[None]:
    page.set_default_timeout(15_000)
    page.set_default_navigation_timeout(30_000)
    request.node._evidence_page = page
    request.node._video_path = page.video.path() if page.video else None
    yield


@pytest.fixture
def app(page: Page, app_url: str) -> SupportApp:
    application = SupportApp(page)
    application.login.open(app_url)
    return application


@pytest.fixture
def admin_app(app: SupportApp, credentials: Credentials) -> SupportApp:
    app.login.login(credentials.admin_id, credentials.admin_password)
    app.tickets.expect_list_visible()
    return app


@pytest.fixture
def guest_app(app: SupportApp, credentials: Credentials) -> SupportApp:
    app.login.login(credentials.guest_id, credentials.guest_password)
    app.header.expect_username(messages.GUEST_HEADER_NAME)
    return app


@pytest.fixture
def second_app(browser, app_url: str, credentials: Credentials) -> Iterator[SupportApp]:
    context = browser.new_context(viewport={"width": 1440, "height": 900})
    page = context.new_page()
    page.set_default_timeout(15_000)
    application = SupportApp(page)
    try:
        application.login.open(app_url)
        application.login.login(credentials.admin_id, credentials.admin_password)
        yield application
    finally:
        context.close()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    outcome = yield
    report = outcome.get_result()
    page = getattr(item, "_evidence_page", None)
    if page is not None and report.when in {"setup", "call"} and (report.passed or report.failed):
        _save_screenshot(item, page, "passed" if report.passed else "failed")
    if report.when == "setup":
        item.rep_setup = report
    elif report.when == "call":
        item.rep_call = report
    elif report.when == "teardown":
        setup_failed = bool(getattr(getattr(item, "rep_setup", None), "failed", False))
        call_failed = bool(getattr(getattr(item, "rep_call", None), "failed", False))
        _finalize_video(item, setup_failed or call_failed)
