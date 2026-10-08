"""New-ticket drawer."""

from __future__ import annotations

import re

import allure
from playwright.sync_api import expect

from constants.locators import TicketDrawerLocators as locators
from pages.base_page import BasePage


class TicketDrawerPage(BasePage):
    """Drawer tạo ticket hai bước. Nút trùng tên được giới hạn trong drawer."""

    @allure.step("Expect the drawer open on step 1")
    def expect_open_on_step1(self) -> None:
        expect(self.loc(locators.DRAWER)).to_have_class(re.compile(r"drawer--open"))
        expect(self.loc(locators.DRAWER)).to_have_css("right", "0px")
        expect(self.loc(locators.STEP1)).to_be_visible()
        expect(self.loc(locators.STEP1_INDICATOR)).to_have_class(re.compile(r"step--active"))
        expect(self.loc(locators.TITLE)).to_have_text("新規チケット作成")
        box = self.loc(locators.DRAWER).bounding_box()
        viewport = self.page.viewport_size
        assert box is not None and viewport is not None, "Drawer box is missing"
        assert box["x"] > viewport["width"] / 2, "Drawer is not on the right side"

    @allure.step("Expect the drawer to be closed")
    def expect_closed(self) -> None:
        expect(self.loc(locators.DRAWER)).not_to_have_class(re.compile(r"drawer--open"))

    @allure.step("Expect Next to be disabled")
    def expect_next_disabled(self) -> None:
        expect(self.loc(locators.NEXT)).to_be_disabled()

    @allure.step("Fill step 1")
    def fill_step1(self, subject: str, priority: str, assignee: str) -> None:
        """Điền bước 1. Ưu tiên/担当者 lấy theo label, scope trong drawer."""
        drawer = self.loc(locators.DRAWER)
        self.fill(locators.SUBJECT, subject)
        self.select_option(locators.PRIORITY, priority, drawer)
        self.select_option(locators.ASSIGNEE, assignee, drawer)

    @allure.step("Read step 1 values")
    def step1_values(self) -> tuple[str, str, str]:
        drawer = self.loc(locators.DRAWER)
        return (
            self.loc(locators.SUBJECT).input_value(),
            self.loc(locators.PRIORITY, drawer).input_value(),
            self.loc(locators.ASSIGNEE, drawer).input_value(),
        )

    @allure.step("Click Next")
    def click_next(self) -> None:
        self.click(locators.NEXT)

    @allure.step("Expect step 2 to show the entered values")
    def expect_step2(self, subject: str, priority: str, assignee: str) -> None:
        expect(self.loc(locators.STEP2)).to_be_visible()
        expect(self.loc(locators.CONFIRM_SUBJECT)).to_have_text(subject)
        expect(self.loc(locators.CONFIRM_PRIORITY)).to_have_text(priority)
        expect(self.loc(locators.CONFIRM_ASSIGNEE)).to_have_text(assignee)

    @allure.step("Click Back")
    def click_back(self) -> None:
        self.click(locators.BACK, self.loc(locators.DRAWER))

    @allure.step("Expect step 1 to be visible")
    def expect_step1_visible(self) -> None:
        expect(self.loc(locators.STEP1)).to_be_visible()

    @allure.step("Click Cancel")
    def click_cancel(self) -> None:
        self.click(locators.CANCEL, self.loc(locators.DRAWER))

    @allure.step("Click Create")
    def click_create(self) -> None:
        """Bấm 作成する trong step 2. Không dùng nút cùng chữ ở modal thông báo."""
        self.click(locators.SUBMIT, self.loc(locators.STEP2))

    @allure.step("Click Create twice in succession")
    def click_create_twice(self) -> None:
        """Bấm liên tiếp hai lần. Trang không khóa nút nên có thể tạo hai dòng."""
        button = self.loc(locators.SUBMIT, self.loc(locators.STEP2))
        button.dispatch_event("click")
        button.dispatch_event("click")
