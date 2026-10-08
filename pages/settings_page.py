"""Settings screen."""

from __future__ import annotations

import allure
from playwright.sync_api import expect

from constants.locators import SettingsLocators as locators
from pages.base_page import BasePage


class SettingsPage(BasePage):
    """Cài đặt: chữ ký tối đa 100 ký tự và toggle thông báo bấm bằng label."""

    @allure.step("Expect the settings screen")
    def expect_screen(self) -> None:
        expect(self.loc(locators.PANEL)).to_be_visible()
        self.expect_visible(locators.HEADING)

    @allure.step("Fill the signature")
    def fill_signature(self, text: str) -> None:
        self.fill(locators.SIGNATURE, text)

    @allure.step("Type one more signature character")
    def type_more(self, character: str) -> None:
        field = self.loc(locators.SIGNATURE)
        field.focus()
        field.press(character)

    @allure.step("Read the signature")
    def signature_value(self) -> str:
        return self.loc(locators.SIGNATURE).input_value()

    @allure.step("Read the signature counter")
    def counter_text(self) -> str:
        return self.loc(locators.COUNTER).inner_text().strip()

    @allure.step("Toggle notifications")
    def toggle_notifications(self) -> None:
        """Bấm label chữ, không bấm input. Input đang 0px nên click/check sẽ thất bại."""
        self.click(locators.TOGGLE)

    @allure.step("Save settings")
    def save(self) -> None:
        """Bấm 保存する trong panel cài đặt, tránh nút cùng chữ ở dialog chi tiết."""
        self.click(locators.SAVE, self.loc(locators.PANEL))
