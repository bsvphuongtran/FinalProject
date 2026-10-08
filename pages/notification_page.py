"""Notification list and the create modal."""

from __future__ import annotations

import re

import allure
from playwright.sync_api import Locator, expect

from constants import messages
from constants.locators import NotificationLocators as locators
from pages.base_page import BasePage


class NotificationPage(BasePage):
    """Danh sách thông báo và hàm ensure_notification_exists (tìm, không có thì tạo)."""

    def _body(self) -> Locator:
        return self.loc(locators.TABLE_BODY)

    @allure.step("Expect the notification list")
    def expect_screen(self) -> None:
        expect(self.loc(locators.PANEL)).to_be_visible()
        self.expect_visible(locators.HEADING)

    @allure.step("Read notification titles")
    def titles(self) -> list[str]:
        rows = self._body().get_by_role("row")
        found: list[str] = []
        for index in range(rows.count()):
            cells = rows.nth(index).get_by_role("cell")
            if cells.count() >= 2:
                found.append(cells.nth(1).inner_text().strip())
        return found

    @allure.step("Search notifications for {keyword}")
    def search(self, keyword: str) -> None:
        """Tìm trong panel thông báo. Nút 検索 được scope để khỏi bấm nhầm màn ticket."""
        self.fill(locators.SEARCH_INPUT, keyword)
        self.click(locators.SEARCH_BUTTON, self.loc(locators.PANEL))

    @allure.step("Expect the notification search to be empty")
    def expect_search_cleared(self) -> None:
        expect(self.loc(locators.SEARCH_INPUT)).to_have_value("")

    @allure.step("Expect notification text {text}")
    def expect_text_visible(self, text: str) -> None:
        expect(self._body()).to_contain_text(text)

    @allure.step("Expect the empty-state create button")
    def expect_empty_create_visible(self) -> None:
        self.expect_visible(locators.EMPTY_CREATE)

    @allure.step("Click the empty-result create button")
    def click_empty_create(self) -> None:
        self.click(locators.EMPTY_CREATE)

    @allure.step("Open the notification create modal")
    def open_create_modal(self) -> None:
        self.click(locators.CREATE_BUTTON)
        self.expect_modal_open()

    @allure.step("Expect the create modal to be open")
    def expect_modal_open(self) -> None:
        expect(self.loc(locators.MODAL)).to_be_visible()
        self.expect_visible(locators.MODAL_TITLE)

    @allure.step("Expect the create modal to be closed")
    def expect_modal_closed(self) -> None:
        expect(self.loc(locators.MODAL)).to_be_hidden()

    @allure.step("Fill the notification form")
    def fill_form(self, title: str, content: str) -> None:
        self.fill(locators.TITLE_INPUT, title)
        self.fill(locators.CONTENT_INPUT, content)

    @allure.step("Expect notification Create to be disabled")
    def expect_submit_disabled(self) -> None:
        expect(self.loc(locators.SUBMIT, self.loc(locators.MODAL))).to_be_disabled()

    @allure.step("Submit the notification form")
    def submit(self) -> None:
        self.click(locators.SUBMIT, self.loc(locators.MODAL))

    @allure.step("Expect notification pagination to be hidden")
    def expect_pagination_hidden(self) -> None:
        """5 thông báo trở xuống thì cả khối phân trang bị ẩn, không assert nút disable."""
        pagination = self.loc(locators.PAGINATION)
        expect(pagination).to_be_hidden()
        expect(self.loc(locators.NEXT_BUTTON, pagination)).to_be_hidden()

    @allure.step("Expect notification pagination to be visible")
    def expect_pagination_visible(self) -> None:
        expect(self.loc(locators.PAGINATION)).to_be_visible()

    @allure.step("Open the next notification page")
    def click_next(self) -> None:
        self.click(locators.NEXT_BUTTON, self.loc(locators.PAGINATION))

    @allure.step("Expect notification page {number} to be selected")
    def expect_page_selected(self, number: int) -> None:
        button = self.loc(locators.PAGINATION).get_by_role(
            "button", name=str(number), exact=True
        )
        expect(button).to_have_class(re.compile(r"page-btn--active"))

    @allure.step("Ensure notification exists: {title}")
    def ensure_notification_exists(self, title: str, content: str) -> None:
        """Tìm theo tiêu đề. Thấy rồi thì dừng. Không thấy thì bấm ＋通知を作成する dưới message rỗng.

        Không dùng has_text trên cả dòng, vì câu "không tìm thấy" có chứa đúng từ khóa vừa tìm.
        """
        self.search(title)
        if title in self.titles():
            return
        self.click_empty_create()
        self.fill_form(title, content)
        self.submit()
        self.expect_toast(messages.NOTIFICATION_CREATED_TOAST)
        self.dismiss_toast(messages.NOTIFICATION_CREATED_TOAST)

    @allure.step("Read notification chip colors")
    def chip_colors(self) -> dict[str, str]:
        colors: dict[str, str] = {}
        for label in ("お知らせ", "警告", "エラー"):
            chip = self.loc(locators.CHIP).filter(has_text=re.compile(rf"^{label}$")).first
            colors[label] = chip.evaluate("el => getComputedStyle(el).backgroundColor")
        return colors
