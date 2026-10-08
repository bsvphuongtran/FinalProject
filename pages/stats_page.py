"""Statistics screen."""

from __future__ import annotations

import allure
from playwright.sync_api import expect

from constants.locators import StatsLocators as locators
from pages.base_page import BasePage


class StatsPage(BasePage):
    """Số liệu giữ nguyên cho đến khi bấm 再集計する. Chỉ đổi tab thì số vẫn cũ."""

    @allure.step("Expect the statistics screen")
    def expect_screen(self) -> None:
        expect(self.loc(locators.PANEL)).to_be_visible()
        self.expect_visible(locators.HEADING)

    @allure.step("Read statistics counts")
    def counts(self) -> dict[str, int]:
        return {
            "total": int(self.loc(locators.TOTAL).inner_text()),
            "未対応": int(self.loc(locators.UNTREATED).inner_text()),
            "対応中": int(self.loc(locators.IN_PROGRESS).inner_text()),
            "完了": int(self.loc(locators.DONE).inner_text()),
        }

    @allure.step("Read bar widths")
    def bar_percents(self) -> dict[str, float]:
        specs = {
            "未対応": locators.BAR_UNTREATED,
            "対応中": locators.BAR_IN_PROGRESS,
            "完了": locators.BAR_DONE,
        }
        widths: dict[str, float] = {}
        for key, spec in specs.items():
            raw = self.loc(spec).evaluate("el => el.style.width || '0'")
            widths[key] = float(str(raw).replace("%", ""))
        return widths

    @allure.step("Click recalculate")
    def recalculate(self) -> None:
        self.click(locators.REFRESH)
