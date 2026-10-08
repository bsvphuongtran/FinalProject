"""Ticket list, including dialogs that are launched from a row."""

from __future__ import annotations

import re

import allure
from playwright.sync_api import Dialog, Locator, Page, expect

from constants import messages
from constants.locators import HeaderLocators
from constants.locators import PreviewFrameLocators
from constants.locators import TicketListLocators as locators
from pages.base_page import BasePage

_COLUMN_SUBJECT = 2
_COLUMN_PRIORITY = 3
_COLUMN_STATUS = 4
_COLUMN_ASSIGNEE = 5
_COLUMN_CREATED = 6


class TicketListPage(BasePage):
    """Ticket table, filters, pagination, and row actions."""

    def _body(self) -> Locator:
        return self.loc(locators.TABLE_BODY)

    def _row(self, subject: str) -> Locator:
        return self._body().get_by_role("row").filter(has_text=subject)

    def _data_rows(self) -> list[Locator]:
        rows = self._body().get_by_role("row")
        found: list[Locator] = []
        for index in range(rows.count()):
            row = rows.nth(index)
            if row.get_by_role("cell").count() >= 8:
                found.append(row)
        return found

    def _column(self, index: int) -> list[str]:
        """Read one body column. Indexes follow the ticket table."""
        return [
            row.get_by_role("cell").nth(index).inner_text().strip()
            for row in self._data_rows()
        ]

    @allure.step("Expect the ticket list to be visible")
    def expect_list_visible(self) -> None:
        expect(self.loc(locators.PANEL)).to_be_visible()
        self.expect_visible(locators.HEADING)

    @allure.step("Expect the ticket list to be hidden")
    def expect_list_hidden(self) -> None:
        expect(self.loc(locators.PANEL)).to_be_hidden()

    @allure.step("Set rows per page to {value}")
    def set_per_page(self, value: str) -> None:
        self.select_option(locators.PER_PAGE, value)

    @allure.step("Count visible ticket rows")
    def visible_row_count(self) -> int:
        return len(self._data_rows())

    @allure.step("Read visible subjects")
    def subjects(self) -> list[str]:
        return self._column(_COLUMN_SUBJECT)

    @allure.step("Read visible priorities")
    def priorities(self) -> list[str]:
        return self._column(_COLUMN_PRIORITY)

    @allure.step("Read visible statuses")
    def statuses(self) -> list[str]:
        return self._column(_COLUMN_STATUS)

    @allure.step("Read visible created dates")
    def created_dates(self) -> list[str]:
        return self._column(_COLUMN_CREATED)

    @allure.step("Read status of {subject}")
    def status_of(self, subject: str) -> str:
        row = self._row(subject)
        expect(row).to_have_count(1)
        return row.get_by_role("cell").nth(_COLUMN_STATUS).inner_text().strip()

    @allure.step("Read the row for {subject}")
    def row_fields(self, subject: str) -> dict[str, str]:
        row = self._row(subject)
        expect(row).to_have_count(1)
        cells = row.get_by_role("cell")
        return {
            "subject": cells.nth(_COLUMN_SUBJECT).inner_text().strip(),
            "priority": cells.nth(_COLUMN_PRIORITY).inner_text().strip(),
            "status": cells.nth(_COLUMN_STATUS).inner_text().strip(),
            "assignee": cells.nth(_COLUMN_ASSIGNEE).inner_text().strip(),
            "created": cells.nth(_COLUMN_CREATED).inner_text().strip(),
        }

    @allure.step("Count rows containing {subject}")
    def count_subject(self, subject: str) -> int:
        return self._row(subject).count()

    @allure.step("Select priority {value}")
    def select_priority(self, value: str) -> None:
        self.select_option(locators.PRIORITY_FILTER, value)

    @allure.step("Select status tab {status}")
    def select_status_tab(self, status: str) -> None:
        """Tab trạng thái là thẻ a không có href, role link không ổn định nên scope theo id."""
        self.loc(locators.STATUS_FILTER).get_by_text(status, exact=True).click()

    @allure.step("Fill the ticket search")
    def fill_search(self, keyword: str) -> None:
        self.fill(locators.SEARCH_INPUT, keyword)

    @allure.step("Click ticket search")
    def click_search(self) -> None:
        """Bấm 検索 trong panel ticket. Nút cùng chữ ở màn thông báo nằm ngoài scope."""
        self.click(locators.SEARCH_BUTTON, self.loc(locators.PANEL))

    @allure.step("Search tickets for {keyword}")
    def search(self, keyword: str) -> None:
        self.fill_search(keyword)
        self.click_search()

    @allure.step("Focus the ticket search field")
    def focus_search(self) -> None:
        self.loc(locators.SEARCH_INPUT).focus()

    @allure.step("Press Enter in the ticket search field")
    def press_enter_in_search(self) -> None:
        self.loc(locators.SEARCH_INPUT).press("Enter")

    @allure.step("Read the focused control name")
    def focused_name(self) -> str:
        return self.page.evaluate(
            """() => {
                const el = document.activeElement;
                if (!el) return '';
                const aria = el.getAttribute('aria-label');
                const text = (el.innerText || '').trim();
                return (aria || text).trim();
            }"""
        )

    @allure.step("Press Tab")
    def press_tab(self) -> None:
        self.page.keyboard.press("Tab")

    @allure.step("Press Shift+Tab")
    def press_shift_tab(self) -> None:
        self.page.keyboard.press("Shift+Tab")

    @allure.step("Focus the first row checkbox and press Space")
    def space_on_first_checkbox(self) -> None:
        checkbox = self._body().get_by_role("checkbox").first
        checkbox.evaluate("el => el.focus()")
        self.page.keyboard.press("Space")

    @allure.step("Expect the first row checkbox to be checked")
    def expect_first_checkbox_checked(self) -> None:
        expect(self._body().get_by_role("checkbox").first).to_be_checked()

    @allure.step("Read chip colors for {labels}")
    def chip_colors(self, labels: tuple[str, ...]) -> dict[str, str]:
        colors: dict[str, str] = {}
        for label in labels:
            chip = self.loc(locators.CHIP).filter(
                has_text=re.compile(rf"^{label}$")
            ).first
            colors[label] = chip.evaluate("el => getComputedStyle(el).backgroundColor")
        return colors

    @allure.step("Click next page")
    def click_next(self) -> None:
        self.click(locators.NEXT_BUTTON, self.loc(locators.PAGINATION_TOP))

    @allure.step("Expect previous page to be enabled")
    def expect_previous_enabled(self) -> None:
        expect(self.loc(locators.PREV_BUTTON, self.loc(locators.PAGINATION_TOP))).to_be_enabled()

    @allure.step("Expect ticket pagination to be hidden")
    def expect_pagination_hidden(self) -> None:
        """Một trang trở xuống thì phân trang bị ẩn (display:none), không phải disable."""
        top = self.loc(locators.PAGINATION_TOP)
        bottom = self.loc(locators.PAGINATION_BOTTOM)
        expect(top).to_be_hidden()
        expect(bottom).to_be_hidden()
        expect(self.loc(locators.NEXT_BUTTON, top)).to_be_hidden()
        expect(self.loc(locators.PREV_BUTTON, top)).to_be_hidden()

    @allure.step("Click the created-date header")
    def click_created_header(self) -> None:
        self.click(locators.CREATED_HEADER)

    @allure.step("Expect created-date sort {direction}")
    def expect_sort(self, direction: str) -> None:
        """Không assert innerText của tiêu đề 作成日 vì icon sort và tooltip bị trộn vào."""
        icon = messages.SORT_ASC_ICON if direction == "asc" else messages.SORT_DESC_ICON
        aria = "ascending" if direction == "asc" else "descending"
        expect(self.loc(locators.SORT_ICON)).to_have_text(icon)
        expect(self.loc(locators.CREATED_HEADER)).to_have_attribute("aria-sort", aria)
        dates = self.created_dates()
        ordered = sorted(dates, reverse=direction == "desc")
        assert dates == ordered, "Created dates are not in the expected order"

    @allure.step("Hover the created-date help icon")
    def hover_created_help(self) -> None:
        self.loc(locators.CREATED_HELP).hover()

    @allure.step("Expect the created-date tooltip")
    def expect_created_tooltip(self, text: str) -> None:
        expect(self.loc(locators.TOOLTIP)).to_be_visible()
        expect(self.loc(locators.TOOLTIP)).to_have_text(text)

    @allure.step("Check the select-all checkbox")
    def check_select_all(self) -> None:
        """Check đúng thẻ input. Icon .cb-box có pointer-events:none nên click icon không ăn."""
        self.loc(locators.SELECT_ALL).check(force=True)

    @allure.step("Expect every visible row checkbox to be checked")
    def expect_all_visible_rows_checked(self) -> None:
        boxes = self._body().get_by_role("checkbox")
        count = boxes.count()
        assert count > 0, "No row checkboxes are visible"
        for index in range(count):
            expect(boxes.nth(index)).to_be_checked()

    @allure.step("Check the row {subject}")
    def check_row(self, subject: str) -> None:
        row = self._row(subject)
        expect(row).to_have_count(1)
        row.get_by_role("checkbox").check(force=True)  # input opacity:0, không click .cb-box

    @allure.step("Uncheck the row {subject}")
    def uncheck_row(self, subject: str) -> None:
        row = self._row(subject)
        expect(row).to_have_count(1)
        row.get_by_role("checkbox").uncheck(force=True)

    @allure.step("Expect {subject} to stay checked")
    def expect_row_checked(self, subject: str) -> None:
        expect(self._row(subject).get_by_role("checkbox")).to_be_checked()

    @allure.step("Expect the bulk bar to be visible")
    def expect_bulk_bar_visible(self) -> None:
        expect(self.loc(locators.BULK_BAR)).to_be_visible()

    @allure.step("Expect the bulk bar to be hidden")
    def expect_bulk_bar_hidden(self) -> None:
        expect(self.loc(locators.BULK_BAR)).to_be_hidden()

    @allure.step("Expect no checked row")
    def expect_no_checked_rows(self) -> None:
        expect(self.loc(locators.CHECKED_ROWS)).to_have_count(0)

    def _run_with_dialog(
        self, accept: bool, action
    ) -> list[tuple[str, str]]:
        seen: list[tuple[str, str]] = []

        def handle(dialog: Dialog) -> None:
            seen.append((dialog.type, dialog.message))
            if accept:
                dialog.accept()
            else:
                dialog.dismiss()

        self.page.on("dialog", handle)
        try:
            action()
        finally:
            self.page.remove_listener("dialog", handle)
        return seen

    @allure.step("Bulk-complete selected rows, accept={accept}")
    def bulk_complete(self, *, accept: bool) -> list[tuple[str, str]]:
        return self._run_with_dialog(accept, lambda: self.click(locators.BULK_COMPLETE))

    @allure.step("Delete {subject}, accept={accept}")
    def delete_row(self, subject: str, *, accept: bool) -> list[tuple[str, str]]:
        """Xóa đúng dòng. Nút 削除 xuất hiện trên mọi dòng nên phải scope theo dòng."""
        row = self._row(subject)
        expect(row).to_have_count(1)
        return self._run_with_dialog(
            accept, lambda: self.click(locators.DELETE_BUTTON, row)
        )

    @allure.step("Open detail for {subject}")
    def open_detail(self, subject: str) -> None:
        row = self._row(subject)
        expect(row).to_have_count(1)
        self.click(locators.DETAIL_BUTTON, row)  # 詳細 trùng mỗi dòng, phải scope theo dòng

    @allure.step("Open the kebab menu for {subject}")
    def open_kebab(self, subject: str) -> None:
        """Mở menu その他の操作 của đúng dòng. Nút này có trên mọi dòng."""
        row = self._row(subject)
        expect(row).to_have_count(1)
        self.click(locators.KEBAB_BUTTON, row)
        expect(self.loc(locators.COMPLETE_ACTION, row)).to_be_visible()

    @allure.step("Expect the kebab menu for {subject} to be closed")
    def expect_kebab_closed(self, subject: str) -> None:
        row = self._row(subject)
        expect(self.loc(locators.COMPLETE_ACTION, row)).to_be_hidden()

    @allure.step("Choose complete for {subject}")
    def choose_complete(self, subject: str) -> None:
        row = self._row(subject)
        expect(row).to_have_count(1)
        self.click(locators.COMPLETE_ACTION, row)

    @allure.step("Click toolbar create")
    def click_toolbar_create(self) -> None:
        self.click(locators.CREATE_BUTTON)

    @allure.step("Expect the empty-state create button")
    def expect_empty_create_visible(self) -> None:
        self.expect_visible(locators.EMPTY_CREATE_BUTTON)

    @allure.step("Click the empty-state create button")
    def click_empty_create(self) -> None:
        self.click(locators.EMPTY_CREATE_BUTTON)

    @allure.step("Expect message {text}")
    def expect_message(self, text: str) -> None:
        expect(self._body()).to_contain_text(text)

    @allure.step("Reassign the owner to {name}")
    def reassign(self, name: str) -> None:
        def handle(dialog: Dialog) -> None:
            assert dialog.type == "prompt", "Reassign dialog is not a prompt"
            dialog.accept(name)

        self.page.once("dialog", handle)
        self.click(locators.REASSIGN)

    @allure.step("Expect reassign result")
    def expect_reassign_result(self, text: str) -> None:
        expect(self.loc(locators.REASSIGN_RESULT)).to_have_text(text)

    @allure.step("Open the print preview popup")
    def open_print_preview(self) -> Page:
        with self.page.expect_popup() as popup_info:
            self.click(locators.PRINT_PREVIEW)
        popup = popup_info.value
        popup.wait_for_load_state("domcontentloaded")
        return popup

    @allure.step("Open the external manual")
    def open_manual(self) -> Page:
        with self.page.expect_popup() as popup_info:
            self.click(locators.OPEN_MANUAL)
        popup = popup_info.value
        popup.wait_for_load_state("domcontentloaded")
        return popup

    @allure.step("Block the external manual host")
    def block_manual_host(self) -> None:
        def abort(route) -> None:
            route.abort("failed")

        self.page.context.route("https://playwright.dev/**", abort)
        self.page.context.route("https://www.playwright.dev/**", abort)

    @allure.step("Apply embedded status {status}")
    def apply_embedded_status(self, status: str) -> str:
        frame = self.page.frame_locator(PreviewFrameLocators.FRAME.value)
        frame.get_by_role("combobox").select_option(label=status)
        frame.get_by_role("button", name="適用", exact=True).click()
        return frame.locator(PreviewFrameLocators.RESULT.value).inner_text()

    @allure.step("Expect the main ticket controls to fit")
    def expect_main_controls_fit(self) -> None:
        self.expect_fits_horizontally(HeaderLocators.LOGO)
        self.expect_fits_horizontally(HeaderLocators.USER_MENU_BUTTON)
        self.expect_fits_horizontally(locators.HEADING)
        self.expect_fits_horizontally(locators.CREATE_BUTTON)
        self.expect_fits_horizontally(locators.SEARCH_INPUT)
        self.expect_no_horizontal_overflow()

    @allure.step("Expect the print preview for {count} tickets")
    def expect_print_preview(self, popup: Page, count: int) -> None:
        expect(popup.get_by_text(messages.PRINT_PREVIEW_HEADING, exact=True)).to_be_visible()
        expect(
            popup.get_by_text(messages.PRINT_PREVIEW_COUNT.format(count=count), exact=True)
        ).to_be_visible()

    @allure.step("Expect the manual page to load")
    def expect_manual_loaded(self, popup: Page) -> None:
        expect(popup).to_have_url(re.compile(r"https://([^/]+\.)?playwright\.dev"))
        expect(popup).to_have_title(re.compile("Playwright"))

    @allure.step("Open a documentation link on the manual page")
    def open_manual_section(self, popup: Page) -> None:
        popup.get_by_role("link", name=re.compile(r"Docs|Get started", re.I)).first.click()
        expect(popup).to_have_url(re.compile(r"playwright\.dev/.+"))

    @allure.step("Expect the browser error page")
    def expect_browser_error_page(self, popup: Page) -> None:
        expect(popup).to_have_url(re.compile(r"chrome-error|chromewebdata"))

    @allure.step("Trigger the browser print event in the preview")
    def print_preview(self, popup: Page) -> bool:
        return bool(
            popup.evaluate(
                """() => {
                    let printed = false;
                    window.addEventListener('beforeprint', () => { printed = true; });
                    window.print();
                    return printed;
                }"""
            )
        )
