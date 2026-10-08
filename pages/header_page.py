"""Application header: logo, tabs, and the user menu."""

from __future__ import annotations

import re

import allure
from playwright.sync_api import expect

from constants.locators import HeaderLocators as locators
from constants.locators import button_named
from pages.base_page import BasePage


class HeaderPage(BasePage):
    """Shared header actions."""

    @allure.step("Open tab {name}")
    def open_tab(self, name: str) -> None:
        """Mở tab theo chữ trong #nav_tabs. Tab là li, không phải button."""
        self.loc(locators.NAV).get_by_text(name, exact=True).click()

    @allure.step("Expect tab {name} to be active")
    def expect_tab_active(self, name: str) -> None:
        tab = self.loc(locators.NAV).get_by_text(name, exact=True)
        expect(tab).to_have_class(re.compile(r"nav-tab--active"))

    @allure.step("Expect header user name {username}")
    def expect_username(self, username: str) -> None:
        expect(self.loc(button_named(username))).to_be_visible()
        expect(self.loc(locators.USER_NAME)).to_have_text(username)

    @allure.step("Open the user menu")
    def open_user_menu(self) -> None:
        self.click(locators.USER_MENU_BUTTON)
        expect(self.loc(locators.USER_MENU)).to_be_visible()

    @allure.step("Expect the user menu to be closed")
    def expect_user_menu_closed(self) -> None:
        expect(self.loc(locators.USER_MENU)).to_be_hidden()

    @allure.step("Expect settings, help, and logout")
    def expect_menu_entries(self) -> None:
        self.expect_visible(locators.SETTINGS_ITEM, self.loc(locators.USER_MENU))
        self.expect_visible(locators.HELP_ITEM, self.loc(locators.USER_MENU))
        self.expect_visible(locators.LOGOUT_ITEM, self.loc(locators.USER_MENU))
        expect(self.loc(locators.USER_MENU).get_by_role("button")).to_have_count(3)

    @allure.step("Click logout")
    def click_logout(self) -> None:
        self.click(locators.LOGOUT_ITEM, self.loc(locators.USER_MENU))

    @allure.step("Click the logo")
    def click_logo(self) -> None:
        self.click(locators.LOGO)

    @allure.step("Click outside open menus")
    def click_outside(self) -> None:
        self.loc(locators.OUTSIDE).click(position={"x": 24, "y": 8})
