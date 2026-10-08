"""Ticket detail dialog."""

from __future__ import annotations

from pathlib import Path

import allure
from playwright.sync_api import expect

from constants.locators import TicketDetailLocators as locators
from pages.base_page import BasePage


class TicketDetailPage(BasePage):
    """Dialog chi tiết. File đính kèm gán bằng set_input_files, không mở hộp thoại OS."""

    @allure.step("Expect the detail dialog to be open")
    def expect_open(self) -> None:
        expect(self.loc(locators.OVERLAY)).to_be_visible()
        self.expect_visible(locators.TITLE)

    @allure.step("Expect the detail dialog to be closed")
    def expect_closed(self) -> None:
        expect(self.loc(locators.OVERLAY)).to_be_hidden()

    @allure.step("Expect detail fields")
    def expect_fields(
        self,
        subject: str,
        priority: str,
        status: str,
        assignee: str,
        created: str,
    ) -> None:
        expect(self.loc(locators.SUBJECT)).to_have_value(subject)
        expect(self.loc(locators.PRIORITY)).to_contain_text(priority)
        expect(self.loc(locators.STATUS)).to_contain_text(status)
        expect(self.loc(locators.ASSIGNEE)).to_have_text(assignee)
        expect(self.loc(locators.CREATED)).to_have_text(created)

    @allure.step("Input detail subject")
    def fill_subject(self, subject: str) -> None:
        self.fill(locators.SUBJECT, subject)

    @allure.step("Read the detail subject")
    def subject_value(self) -> str:
        return self.loc(locators.SUBJECT).input_value()

    @allure.step("Expect the detail save button to be disabled")
    def expect_save_disabled(self) -> None:
        expect(self.loc(locators.SAVE_BUTTON, self.loc(locators.OVERLAY))).to_be_disabled()

    @allure.step("Close the detail dialog")
    def click_close(self) -> None:
        self.click(locators.CLOSE_BUTTON)

    @allure.step("Upload a file through the hidden input")
    def upload(self, path: Path) -> None:
        """Gán file bằng set_input_files. Input đang display:none, không mở hộp thoại OS."""
        self.loc(locators.FILE_INPUT).set_input_files(str(path))

    @allure.step("Expect file preview {label}")
    def expect_file_preview(self, label: str) -> None:
        expect(self.loc(locators.FILE_PREVIEW)).to_be_visible()
        expect(self.loc(locators.FILE_NAME)).to_have_text(label)
        self.expect_visible(locators.REMOVE_FILE)

    @allure.step("Expect no file preview")
    def expect_no_preview(self) -> None:
        expect(self.loc(locators.FILE_PREVIEW)).to_be_hidden()

    @allure.step("Expect file error {message}")
    def expect_file_error(self, message: str) -> None:
        expect(self.loc(locators.FILE_ERROR)).to_be_visible()
        expect(self.loc(locators.FILE_ERROR)).to_have_text(message)
