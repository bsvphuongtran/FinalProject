"""Login screen."""

from __future__ import annotations

import allure
from playwright.sync_api import expect

from constants.locators import LoginLocators as locators
from pages.base_page import BasePage


class LoginPage(BasePage):
    """Màn hình đăng nhập. Không ghi mật khẩu vào tên step."""

    @allure.step("Open the application")
    def open(self, url: str) -> None:
        self.page.goto(url, wait_until="domcontentloaded")
        self.expect_login_screen()

    @allure.step("Expect the login screen")
    def expect_login_screen(self) -> None:
        self.expect_visible(locators.LOGIN_HEADING)
        self.expect_visible(locators.ID_INPUT)
        self.expect_visible(locators.PASSWORD_INPUT)
        self.expect_visible(locators.LOGIN_BUTTON)

    @allure.step("Input user id")
    def fill_id(self, user_id: str) -> None:
        self.fill(locators.ID_INPUT, user_id)

    @allure.step("Input password")
    def fill_password(self, password: str) -> None:
        self.fill(locators.PASSWORD_INPUT, password)

    @allure.step("Expect the login button to be disabled")
    def expect_login_disabled(self) -> None:
        expect(self.loc(locators.LOGIN_BUTTON)).to_be_disabled()

    @allure.step("Expect the login button to be enabled")
    def expect_login_enabled(self) -> None:
        expect(self.loc(locators.LOGIN_BUTTON)).to_be_enabled()

    @allure.step("Click the login button")
    def submit(self) -> None:
        self.click(locators.LOGIN_BUTTON)

    @allure.step("Log in")
    def login(self, user_id: str, password: str) -> None:
        self.fill_id(user_id)
        self.fill_password(password)
        self.submit()
        self.expect_main_visible()

    @allure.step("Expect the login error")
    def expect_error(self, message: str) -> None:
        expect(self.loc(locators.LOGIN_ERROR)).to_be_visible()
        expect(self.loc(locators.LOGIN_ERROR)).to_contain_text(message)

    @allure.step("Expect the main screen to be hidden")
    def expect_main_hidden(self) -> None:
        expect(self.loc(locators.MAIN_SECTION)).to_be_hidden()

    @allure.step("Expect the main screen to be visible")
    def expect_main_visible(self) -> None:
        expect(self.loc(locators.MAIN_SECTION)).to_be_visible()
        expect(self.loc(locators.LOGIN_SECTION)).to_be_hidden()
