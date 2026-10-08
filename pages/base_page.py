"""Shared Playwright actions. Screen classes add the domain steps."""

from __future__ import annotations

import random
import string
import time

import allure
from playwright.sync_api import Locator, Page, expect

from constants.locators import By, ToastLocators


class BasePage:
    """Browser primitives used by every screen."""

    def __init__(self, page: Page) -> None:
        self.page = page

    def loc(self, spec: By, scope: Locator | None = None) -> Locator:
        """Resolve a catalog entry. Tests never call this."""
        root: Page | Locator = self.page if scope is None else scope
        if spec.kind == "role":
            if spec.name is None:
                return root.get_by_role(spec.value)
            return root.get_by_role(spec.value, name=spec.name, exact=spec.exact)
        if spec.kind == "placeholder":
            return root.get_by_placeholder(spec.value, exact=spec.exact)
        if spec.kind == "text":
            return root.get_by_text(spec.value, exact=spec.exact)
        if spec.kind == "label":
            return root.get_by_label(spec.value, exact=spec.exact)
        if spec.kind == "css":
            return root.locator(spec.value)
        raise ValueError(f"Unsupported locator kind: {spec.kind}")

    @allure.step("Click")
    def click(self, spec: By, scope: Locator | None = None) -> None:
        self.loc(spec, scope).click()

    @allure.step("Fill input")
    def fill(self, spec: By, value: str, scope: Locator | None = None) -> None:
        self.loc(spec, scope).fill(value)

    @allure.step("Select option")
    def select_option(self, spec: By, value: str, scope: Locator | None = None) -> None:
        self.loc(spec, scope).select_option(value=value)

    @allure.step("Expect element to be visible")
    def expect_visible(self, spec: By, scope: Locator | None = None) -> None:
        expect(self.loc(spec, scope)).to_be_visible()

    @allure.step("Expect element text")
    def expect_text(self, spec: By, text: str, scope: Locator | None = None) -> None:
        expect(self.loc(spec, scope)).to_have_text(text)

    def random_chars(self, length: int) -> str:
        """Build a random alphanumeric string of the requested length."""
        alphabet = string.ascii_letters + string.digits
        return "".join(random.choice(alphabet) for _ in range(length))

    def random_data_input_field(self, length: int) -> str:
        """Build random field data of the requested length."""
        return self.random_chars(length)

    def _toast(self, message: str) -> Locator:
        return self.loc(ToastLocators.ITEM).filter(has_text=message)

    @allure.step("Expect toast: {message}")
    def expect_toast(self, message: str) -> None:
        expect(self._toast(message)).to_be_visible()

    @allure.step("Dismiss toast: {message}")
    def dismiss_toast(self, message: str) -> None:
        self._toast(message).get_by_role("button", name="閉じる", exact=True).click()
        expect(self._toast(message)).to_be_hidden()

    @allure.step("Measure toast auto-hide: {message}")
    def seconds_until_toast_hides(self, message: str) -> float:
        toast = self._toast(message)
        expect(toast).to_be_visible()
        started = time.monotonic()
        expect(toast).to_be_hidden(timeout=8_000)
        return time.monotonic() - started

    @allure.step("Set browser offline={offline}")
    def set_offline(self, offline: bool) -> None:
        self.page.context.set_offline(offline)

    @allure.step("Install fixed clock {iso_time}")
    def install_clock(self, iso_time: str) -> None:
        self.page.clock.install(time=iso_time)

    @allure.step("Reload the page")
    def reload(self) -> None:
        self.page.reload(wait_until="domcontentloaded")

    @allure.step("Set viewport {width}x{height}")
    def set_viewport(self, width: int, height: int) -> None:
        self.page.set_viewport_size({"width": width, "height": height})

    @allure.step("Set CSS zoom {zoom}")
    def set_zoom(self, zoom: str) -> None:
        self.page.evaluate(
            "(value) => { document.documentElement.style.zoom = value; }",
            zoom,
        )

    def track_page_errors(self) -> list[str]:
        """Collect uncaught page exceptions for crash checks."""
        errors: list[str] = []
        self.page.on("pageerror", lambda error: errors.append(str(error)))
        return errors

    @allure.step("Expect an error alert or a retry instruction")
    def expect_error_or_retry_feedback(self) -> None:
        """The specification allows either an error alert or a retry instruction."""
        candidates = (
            self.page.get_by_role("alert"),
            self.page.get_by_text("再試行", exact=False),
            self.page.get_by_text("通信失敗", exact=False),
        )
        found = False
        for candidate in candidates:
            if candidate.count() and candidate.first.is_visible():
                found = True
                break
        assert found, "Error or retry feedback is not visible"

    @allure.step("Expect no horizontal page overflow")
    def expect_no_horizontal_overflow(self) -> None:
        metrics = self.page.evaluate(
            """() => ({
                scrollWidth: document.documentElement.scrollWidth,
                innerWidth: window.innerWidth
            })"""
        )
        assert metrics["scrollWidth"] <= metrics["innerWidth"] + 1, (
            f"Page overflows horizontally: {metrics}"
        )

    @allure.step("Expect control to fit the viewport width")
    def expect_fits_horizontally(self, spec: By, scope: Locator | None = None) -> None:
        locator = self.loc(spec, scope)
        expect(locator).to_be_visible()
        box = locator.bounding_box()
        viewport = self.page.viewport_size
        assert box is not None, "Control has no box"
        assert viewport is not None, "Viewport is not set"
        assert box["x"] >= -1, "Control starts outside the left edge"
        assert box["x"] + box["width"] <= viewport["width"] + 1, (
            "Control extends past the right edge"
        )
