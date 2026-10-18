"""One test per row on the Testcases sheet."""

from __future__ import annotations

import math
import re
import shutil

import allure
import pytest

from constants import messages
from helpers import description_md
from helpers.sample_files import write_sample
from pages.support_app import SupportApp
import os

# APP_URL = "https://bsv-nhungnguyen.github.io/bai_tap_17082026.html"
APP_URL = os.getenv("APP_URL")

###NNTT: em nghĩ nên sử dụng thống nhất URL ở 1 nguồn duy nhất để dễ quản lý và maintain (.env)


def _passed(summary: str) -> None:
    with allure.step(f"[PASSED] {summary}"):
        pass


@allure.feature("Testcases")
@allure.story("Testcases GD01_001-GD03.1-06")
@allure.link(APP_URL, name="APP_URL")
@description_md(
    """
    - **前提条件**: Automation _ Finnal Project.xlsx / sheet Testcases
    - **テスト手順**: ID GD01_001 から GD03.1-06（88件）
    - **期待する結果**: 各テストの description を参照
    """
)
class TestTestcases:
###NNTT: nên chia thành nhiều file testcase để dễ quản lý và dễ đọc, dễ maintain (có thể chia theo Screen Name hoặc Category)
### Em nghĩ lý tưởng nhất là mỗi file test chỉ nên chứa tầm 500 lines code.
    """Mỗi hàm tương ứng một dòng trên sheet Testcases."""

    # Back/forward: trang không gọi history.pushState, spec không nói state nào phải còn.
    @allure.title("Testcases_001: GD01_001 browser back and forward")
    @description_md(
        """
        - **前提条件**: 複数画面を遷移済み
        - **テスト手順**: 1. ブラウザの戻るボタンを押下する
          2. 必要に応じて進むボタンを押下する
          3. 各画面の状態を確認する
        - **期待する結果**: ブラウザ履歴に従って正しく画面遷移し、ログイン状態や入力状態が仕様どおりに処理される
        """
    )
    def test_gd01_001_browser_back_forward_handles_history_state(self) -> None:
        pytest.skip(
            "Spec incomplete for GD01_001: the page never calls history.pushState, "
            "and the expected result does not define which history entries or which "
            "login/input state must remain. Reliable back/forward automation is not possible."
        )

    # Layout không tràn ngang ở nhiều kích thước viewport.
    @allure.title("Testcases_002: Others_01 layout at several viewport sizes")
    @description_md(
        """
        - **前提条件**: チケット一覧画面を表示中
        - **テスト手順**: 1. 異なる解像度・アスペクト比の実端末または実ブラウザで画面を表示する
          2. ヘッダー、テーブル、ボタン、ダイアログ等を確認する
        - **期待する結果**: 重要なUI要素が画面外にはみ出さず、重なりや表示崩れが発生しない
        """
    )
    def test_others_01_layout_stays_inside_viewport_at_multiple_sizes(
        self, admin_app: SupportApp
    ) -> None:
        problems: list[str] = []
        for width, height in ((1920, 1080), (1366, 768), (390, 844)):
            admin_app.tickets.set_viewport(width, height)
            try:
                admin_app.tickets.expect_main_controls_fit()
            except AssertionError as exc:
                problems.append(f"{width}x{height}: {exc}")
        assert not problems, "Layout overflows: " + " | ".join(problems)
        _passed("Important controls stay inside 1920, 1366, and 390 widths")

    # Đổi đồng hồ thì ngày tạo mới theo format, ngày seed giữ nguyên.
    @allure.title("Testcases_003: Others_02 dates keep their format after a clock change")
    @description_md(
        """
        - **前提条件**: ログイン済み・日時表示を含む画面を表示中
        - **テスト手順**: 1. OSのシステム時刻を変更する
          2. アプリを再読み込みする
          3. 作成日・更新日等の日時表示を確認する
        - **期待する結果**: 日時が仕様で定義されたタイムゾーン・フォーマットに従って正しく表示される
        """
    )
    def test_others_02_created_dates_follow_defined_format_when_clock_changes(
        self, admin_app: SupportApp, credentials
    ) -> None:
        before = admin_app.tickets.created_dates()
        admin_app.tickets.install_clock("2030-06-15T03:00:00Z")
        admin_app.tickets.reload()
        admin_app.login.login(credentials.admin_id, credentials.admin_password)
        after = admin_app.tickets.created_dates()
        assert after == before, "Created dates changed when the clock changed"
        assert after, "Created dates are missing"
        assert all(re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) for value in after), (
            "Created dates are not in YYYY-MM-DD format"
        )
        _passed("Created dates stay YYYY-MM-DD after the clock change")

    # Tìm thông báo 0 kết quả thì nút tạo mới dưới message phải mở modal.
    @allure.title("Testcases_004: GD02.1-01 zero-hit notification search opens create")
    @description_md(
        """
        - **前提条件**: 通知一覧画面を表示中
        - **テスト手順**: 1. 存在しないキーワードで検索する
          2. 「検索条件に一致する通知が見つかりません」の下にある「＋通知を作成する」ボタンを押下する
        - **期待する結果**: 通知作成モーダルが開く（ツールバーの作成ボタンと同じ動作）
        """
    )
    def test_gd021_01_zero_notification_search_opens_create_modal(
        self, admin_app: SupportApp
    ) -> None:
        keyword = "missing-" + admin_app.notifications.random_chars(8)
        admin_app.header.open_tab("通知")
        admin_app.notifications.search(keyword)
        admin_app.notifications.expect_text_visible(messages.NOTIFICATION_NOT_FOUND)
        admin_app.notifications.click_empty_create()
        admin_app.notifications.expect_modal_open()
        _passed("The not-found create button opens the notification modal")

    # Popup in hiện đúng số lượng ticket.
    @allure.title("Testcases_005: GD03.3-01 print preview popup shows the ticket count")
    @description_md(
        """
        - **前提条件**: チケット一覧画面を表示中
        - **テスト手順**: 1. 「印刷プレビューを開く（新しいウィンドウ）」ボタンを押下する
        - **期待する結果**: 新しいポップアップウィンドウが開き、印刷プレビュー内容（対象チケット数）が表示される
        """
    )
    def test_gd033_01_print_preview_popup_shows_ticket_count(
        self, admin_app: SupportApp
    ) -> None:
        admin_app.tickets.set_per_page("50")
        count = admin_app.tickets.visible_row_count()
        popup = admin_app.tickets.open_print_preview()
        try:
            admin_app.tickets.expect_print_preview(popup, count)
        finally:
            popup.close()
        _passed("Print preview popup shows the ticket count")

    # Chọn 25 dòng/trang thì thấy đủ 12 ticket.
    @allure.title("Testcases_006: GD02.4-01 page size 25 shows all 12 tickets")
    @description_md(
        """
        - **前提条件**: チケット一覧画面を表示中
        - **テスト手順**: 1. 「表示件数」プルダウンで25を選択する
        - **期待する結果**: 12件全てが1ページに表示される
        """
    )
    def test_gd024_01_per_page_25_shows_all_twelve_tickets(
        self, admin_app: SupportApp
    ) -> None:
        admin_app.tickets.set_per_page("25")
        assert admin_app.tickets.visible_row_count() == 12, "All 12 tickets are not on one page"
        admin_app.tickets.expect_pagination_hidden()
        _passed("Page size 25 shows all 12 tickets")

    # Lọc ưu tiên 高 thì còn 5 ticket.
    @allure.title("Testcases_007: GD02.4-02 high priority filter shows 5 tickets")
    @description_md(
        """
        - **前提条件**: チケット一覧画面を表示中
        - **テスト手順**: 1. 優先度プルダウンで「高」を選択する
        - **期待する結果**: 優先度が「高」のチケットのみ表示される（5件）
        """
    )
    def test_gd024_02_priority_high_filter_shows_five_tickets(
        self, admin_app: SupportApp
    ) -> None:
        admin_app.tickets.select_priority(messages.PRIORITY_HIGH)
        priorities = admin_app.tickets.priorities()
        assert priorities == [messages.PRIORITY_HIGH] * 5, "High-priority filter is not 5 rows"
        _passed("Only the 5 high-priority tickets are shown")

    # Ô chữ ký dừng ở 100 ký tự.
    @allure.title("Testcases_008: GD02.3-001 signature stops at 100 characters")
    @description_md(
        """
        - **前提条件**: 設定画面を表示中
        - **テスト手順**: 1. 署名欄に100文字を超えるテキストを入力しようとする
        - **期待する結果**: 最大100文字までしか入力できず、カウンター表示が「100/100文字」で止まる
        """
    )
    def test_gd023_001_signature_stops_at_100_characters(
        self, admin_app: SupportApp
    ) -> None:
        text = admin_app.settings.random_chars(100)
        extra = admin_app.settings.random_chars(1)
        admin_app.header.open_tab("設定")
        admin_app.settings.fill_signature(text)
        admin_app.settings.type_more(extra)
        assert admin_app.settings.signature_value() == text, "Signature accepted more than 100 characters"
        assert admin_app.settings.counter_text() == messages.SIGNATURE_COUNTER_FULL, (
            "Counter did not stop at 100/100文字"
        )
        _passed("Signature stops at 100 characters")

    # Sang trang 2 còn 2 ticket và nút 前へ được bật.
    @allure.title("Testcases_009: GD02.1-02 next page shows the remaining 2 tickets")
    @description_md(
        """
        - **前提条件**: 1ページの表示件数が10件（デフォルト）
        - **テスト手順**: 1. 「次へ」ボタンを押下する
        - **期待する結果**: 2ページ目（残り2件）が表示され、「前へ」ボタンが活性化する
        """
    )
    def test_gd021_02_next_page_shows_remaining_two_and_enables_previous(
        self, admin_app: SupportApp
    ) -> None:
        admin_app.tickets.click_next()
        assert admin_app.tickets.visible_row_count() == 2, "Page 2 does not show the remaining 2 tickets"
        admin_app.tickets.expect_previous_enabled()
        _passed("Page 2 shows 2 tickets and Previous is enabled")

    # Nút tạo ở trạng thái rỗng mở cùng drawer với nút trên toolbar.
    @allure.title("Testcases_010: GD02.1-03 empty-state create opens the drawer")
    @description_md(
        """
        - **前提条件**: guestでログイン済み・チケット一覧が空の状態
        - **テスト手順**: 1. 空状態に表示されている「＋新規チケット作成」ボタンを押下する
        - **期待する結果**: ツールバーの「＋新規チケット作成」ボタンと同じ新規チケット作成ドロワーが開く
        """
    )
    def test_gd021_03_empty_state_create_opens_the_same_drawer(
        self, guest_app: SupportApp
    ) -> None:
        guest_app.tickets.click_empty_create()
        guest_app.drawer.expect_open_on_step1()
        _passed("The empty-state button opens the new-ticket drawer")

    # Xác nhận xóa thì dòng biến mất và có toast.
    @allure.title("Testcases_011: GD03.1-01 delete confirm removes the row")
    @description_md(
        """
        - **前提条件**: チケット一覧画面を表示中
        - **テスト手順**: 1. 任意の行の「削除」ボタンを押下する
          2. 確認ダイアログ（confirm）で「OK」を押下する
        - **期待する結果**: 該当行が一覧から削除され、トースト通知「チケットを削除しました。」が表示される
        """
    )
    def test_gd031_01_delete_confirm_ok_removes_row_and_shows_toast(
        self, admin_app: SupportApp
    ) -> None:
        subject = admin_app.tickets.subjects()[0]
        dialogs = admin_app.tickets.delete_row(subject, accept=True)
        assert dialogs and dialogs[0][0] == "confirm", "Delete did not open a confirm dialog"
        assert admin_app.tickets.count_subject(subject) == 0, "Deleted row is still listed"
        admin_app.tickets.expect_toast(messages.DELETE_TOAST)
        _passed("Confirming delete removes the row and shows the toast")

    # Tìm thông báo theo từ khóa chỉ còn bản ghi khớp.
    @allure.title("Testcases_012: GD02.3-002 notification keyword search")
    @description_md(
        """
        - **前提条件**: 通知一覧画面を表示中
        - **テスト手順**: 1. 検索欄にタイトルの一部を入力する
          2. 「検索」ボタンを押下する
        - **期待する結果**: タイトルまたは内容に一致する通知のみ表示される
        """
    )
    def test_gd023_002_notification_keyword_search_shows_matches_only(
        self, admin_app: SupportApp
    ) -> None:
        admin_app.header.open_tab("通知")
        admin_app.notifications.search(messages.NOTIFICATION_KEYWORD)
        titles = admin_app.notifications.titles()
        assert titles, "No notification matched the keyword"
        assert all(messages.NOTIFICATION_KEYWORD in title for title in titles), (
            "A non-matching notification is still shown"
        )
        _passed("Notification search shows only matching titles")

    # Bấm 作成日 lần hai thì sort giảm dần. Không assert innerText của header.
    @allure.title("Testcases_013: GD02.1-04 second created-date click sorts descending")
    @description_md(
        """
        - **前提条件**: 「作成日」列見出しを1回押下済み
        - **テスト手順**: 1. 「作成日」列見出しをもう一度押下する
        - **期待する結果**: 作成日の降順に並び替わり、ソートアイコンが下向き矢印になる
        """
    )
    def test_gd021_04_second_created_date_click_sorts_descending(
        self, admin_app: SupportApp
    ) -> None:
        admin_app.tickets.click_created_header()
        admin_app.tickets.click_created_header()
        admin_app.tickets.expect_sort("desc")
        _passed("The second click sorts created dates descending")

    # Màn login có ô ID, mật khẩu và nút ログイン.
    @allure.title("Testcases_014: GD01_002 login screen shows id, password, and login")
    @description_md(
        """
        - **前提条件**: ブラウザでページを開く
        - **テスト手順**: 1. ページを開く
        - **期待する結果**: ログイン画面が表示される（ID・パスワード入力欄、ログインボタン）
        """
    )
    def test_gd01_002_login_screen_shows_id_password_and_login_button(
        self, app: SupportApp
    ) -> None:
        app.login.expect_login_screen()
        _passed("The login screen shows ID, password, and the login button")

    # Prompt đổi người phụ trách phản ánh đúng tên vừa nhập.
    @allure.title("Testcases_015: GD03.1-02 reassign prompt shows the entered name")
    @description_md(
        """
        - **前提条件**: チケット一覧画面を表示中
        - **テスト手順**: 1. 「担当者を再割り当てする」ボタンを押下する
          2. promptダイアログに任意の名前を入力してOKを押下する
        - **期待する結果**: 入力した名前が画面上の再割り当て結果として反映される
        """
    )
    def test_gd031_02_reassign_prompt_reflects_entered_name(
        self, admin_app: SupportApp
    ) -> None:
        admin_app.tickets.reassign(messages.REASSIGN_NAME)
        admin_app.tickets.expect_reassign_result(
            messages.REASSIGN_RESULT.format(name=messages.REASSIGN_NAME)
        )
        _passed("The entered name is shown as the reassignment result")

    # Bấm ra ngoài thì menu kebab đóng.
    @allure.title("Testcases_016: GD02.1-05 outside click closes the kebab menu")
    @description_md(
        """
        - **前提条件**: いずれかの行のケバブメニューを表示中
        - **テスト手順**: 1. メニュー外の任意の場所を押下する
        - **期待する結果**: 開いていたケバブメニューが閉じる
        """
    )
    def test_gd021_05_outside_click_closes_kebab_menu(self, admin_app: SupportApp) -> None:
        subject = admin_app.tickets.subjects()[0]
        admin_app.tickets.open_kebab(subject)
        admin_app.header.click_outside()
        admin_app.tickets.expect_kebab_closed(subject)
        _passed("Clicking outside closes the kebab menu")

    # Hủy xóa thì dòng vẫn còn.
    @allure.title("Testcases_017: GD03.1-03 delete cancel keeps the row")
    @description_md(
        """
        - **前提条件**: チケット一覧画面を表示中
        - **テスト手順**: 1. 「削除」ボタンを押下する
          2. 確認ダイアログで「キャンセル」を押下する
        - **期待する結果**: 行は削除されず、一覧に残ったままである
        """
    )
    def test_gd031_03_delete_cancel_keeps_the_row(self, admin_app: SupportApp) -> None:
        subject = admin_app.tickets.subjects()[0]
        admin_app.tickets.delete_row(subject, accept=False)
        assert admin_app.tickets.count_subject(subject) == 1, "Cancelled delete removed the row"
        _passed("Cancelling delete keeps the row")

    # Bấm 作成日 lần đầu thì sort tăng dần theo icon và aria-sort.
    @allure.title("Testcases_018: GD02.1-06 created-date click sorts ascending")
    @description_md(
        """
        - **前提条件**: チケット一覧画面を表示中
        - **テスト手順**: 1. 「作成日」列見出しを押下する
        - **期待する結果**: 作成日の昇順に並び替わり、ソートアイコンが上向き矢印になる
        """
    )
    def test_gd021_06_created_date_click_sorts_ascending(self, admin_app: SupportApp) -> None:
        admin_app.tickets.click_created_header()
        admin_app.tickets.expect_sort("asc")
        _passed("The first click sorts created dates ascending")

    # Tạo thông báo thì bản ghi mới nằm trên cùng.
    @allure.title("Testcases_019: GD02.3-003 creating a notification adds it at the top")
    @description_md(
        """
        - **前提条件**: 通知作成モーダルを表示中
        - **テスト手順**: 1. タイトル・内容を入力する（種別はデフォルトのまま）
          2. 「作成する」ボタンを押下する
        - **期待する結果**: モーダルが閉じ、一覧の先頭に新しい通知が追加され、検索条件がクリアされて新規作成分が表示される。トースト通知「通知を作成しました。」が表示される
        """
    )
    def test_gd023_003_create_notification_adds_it_at_the_top(
        self, admin_app: SupportApp
    ) -> None:
        title = "AUTO" + admin_app.notifications.random_chars(8)
        content = admin_app.notifications.random_data_input_field(12)
        admin_app.header.open_tab("通知")
        admin_app.notifications.open_create_modal()
        admin_app.notifications.fill_form(title, content)
        admin_app.notifications.submit()
        admin_app.notifications.expect_modal_closed()
        admin_app.notifications.expect_search_cleared()
        assert admin_app.notifications.titles()[0] == title, "New notification is not first"
        admin_app.notifications.expect_toast(messages.NOTIFICATION_CREATED_TOAST)
        _passed("The new notification is first and the toast is shown")

    # Từ khóa không có ticket thì hiện message không tìm thấy.
    @allure.title("Testcases_020: GD02.8-01 unknown keyword shows the no-ticket message")
    @description_md(
        """
        - **前提条件**: チケット一覧画面を表示中
        - **テスト手順**: 1. 検索欄に存在しないキーワードを入力する
          2. 「検索」ボタンを押下する
        - **期待する結果**: 「該当するチケットがありません」というメッセージが表示される
        """
    )
    def test_gd028_01_unknown_keyword_shows_no_ticket_message(
        self, admin_app: SupportApp
    ) -> None:
        admin_app.tickets.search("zzz-no-such-ticket")
        admin_app.tickets.expect_message(messages.NO_TICKET_MATCH)
        _passed("An unknown keyword shows the no-ticket message")

    # Bấm ra ngoài thì menu user đóng.
    @allure.title("Testcases_021: GD02.1-07 outside click closes the user menu")
    @description_md(
        """
        - **前提条件**: ユーザーメニューを表示中
        - **テスト手順**: 1. メニュー外の任意の場所を押下する
        - **期待する結果**: ユーザーメニューが閉じる
        """
    )
    def test_gd021_07_outside_click_closes_user_menu(self, admin_app: SupportApp) -> None:
        admin_app.header.open_user_menu()
        admin_app.header.click_outside()
        admin_app.header.expect_user_menu_closed()
        _passed("Clicking outside closes the user menu")

    # Hủy drawer thì dữ liệu vừa nhập bị bỏ.
    @allure.title("Testcases_022: GD02.1-08 drawer cancel discards the input")
    @description_md(
        """
        - **前提条件**: ドロワーのStep1を表示中
        - **テスト手順**: 1. 件名等を入力する
          2. 「キャンセル」ボタンを押下する
          3. 再度「＋新規チケット作成」ボタンを押下する
        - **期待する結果**: ドロワーが閉じ、一覧に追加されない。再度開くと入力欄が空になっている
        """
    )
    def test_gd021_08_drawer_cancel_discards_input(self, admin_app: SupportApp) -> None:
        subject = "AUTO" + admin_app.drawer.random_chars(8)
        admin_app.tickets.click_toolbar_create()
        admin_app.drawer.fill_step1(subject, messages.PRIORITY_HIGH, "佐藤")
        admin_app.drawer.click_cancel()
        admin_app.drawer.expect_closed()
        assert admin_app.tickets.count_subject(subject) == 0, "Cancelled ticket was added"
        admin_app.tickets.click_toolbar_create()
        assert admin_app.drawer.step1_values() == ("", "", ""), "Reopened drawer kept the old input"
        _passed("Cancel closes the drawer and the next open is empty")

    # Menu user có 設定, ヘルプ và ログアウト.
    @allure.title("Testcases_023: GD02.1-09 user menu shows settings, help, and logout")
    @description_md(
        """
        - **前提条件**: ログイン済み
        - **テスト手順**: 1. ヘッダー右上のユーザー名（田中 太郎（管理者））を押下する
        - **期待する結果**: 設定・ヘルプ・ログアウトの3項目を含むメニューが表示される
        """
    )
    def test_gd021_09_user_menu_shows_settings_help_and_logout(
        self, admin_app: SupportApp
    ) -> None:
        admin_app.header.expect_username(messages.ADMIN_HEADER_NAME)
        admin_app.header.open_user_menu()
        admin_app.header.expect_menu_entries()
        _passed("The user menu shows settings, help, and logout")

    # Đăng xuất ở trình duyệt A. Kỳ vọng B phải đăng nhập lại nếu có session chung.
    @allure.title("Testcases_024: GD03.3-02 logout in one browser invalidates the other")
    @description_md(
        """
        - **前提条件**: 同一アカウントで複数のブラウザまたはタブからログインしている
        - **テスト手順**: 1. ブラウザAでログアウトする
          2. ブラウザBでログイン後の画面を操作する
        - **期待する結果**: 仕様に従ってセッション無効化が反映され、必要に応じて再ログインを要求される
        """
    )
    def test_gd033_02_logout_in_one_browser_invalidates_the_other(
        self, admin_app: SupportApp, second_app: SupportApp, request: pytest.FixtureRequest
    ) -> None:
        admin_app.header.open_user_menu()
        admin_app.header.click_logout()
        admin_app.login.expect_login_screen()
        # NNTT: trường hợp case mở nhiều tab thì nên có step gọi sang tab khác để check -> mục đích để khi phát sinh lỗi thì có thể chụp màn hình đúng vị trí lỗi. 
        request.node._evidence_page = second_app.page
        second_app.header.open_tab("統計")
        second_app.login.expect_login_screen()
        _passed("Logout in browser A requires browser B to log in again")

    # Offline rồi thao tác: mong có lỗi hoặc hướng dẫn thử lại, app không crash.
    @allure.title("Testcases_025: Others_03 offline operation shows an error and does not crash")
    @description_md(
        """
        - **前提条件**: ログイン済み・チケット一覧画面を表示中
        - **テスト手順**: 1. PCの実ネットワーク接続を切断する
          2. 一覧取得や更新などの通信を伴う操作を行う
        - **期待する結果**: 通信失敗が適切に処理され、ユーザーにエラーまたは再試行方法が提示される。アプリがクラッシュしない
        """
    )
    def test_others_03_offline_operation_shows_error_without_crash(
        self, admin_app: SupportApp
    ) -> None:
        errors = admin_app.tickets.track_page_errors()
        admin_app.tickets.set_offline(True)
        admin_app.tickets.search(messages.SEARCH_KEYWORD)
        admin_app.tickets.expect_list_visible()
        assert not errors, "Page crashed while offline"
        admin_app.tickets.expect_error_or_retry_feedback()
        _passed("Offline search shows error or retry feedback without a crash")

    # Admin đăng nhập thấy danh sách và 10 dòng ở trang đầu.
    @allure.title("Testcases_026: GD01_003 admin sees the ticket list with 10 rows")
    @description_md(
        """
        - **前提条件**: admin/admin123でログイン済み
        - **テスト手順**: 1. 画面表示を確認する
        - **期待する結果**: チケット一覧画面（「チケット一覧」タブがアクティブ）が表示され、10件のチケットが表示される
        """
    )
    def test_gd01_003_admin_login_shows_ticket_list_with_ten_rows(
        self, admin_app: SupportApp
    ) -> None:
        admin_app.header.expect_tab_active("チケット一覧")
        admin_app.tickets.expect_list_visible()
        assert admin_app.tickets.visible_row_count() == 10, "The first page does not show 10 tickets"
        _passed("The ticket tab is active and 10 tickets are shown")

    # Thông báo tạo bằng guest không xuất hiện sau khi đăng nhập admin.
    @allure.title("Testcases_027: GD02.8-02 a guest notification is hidden from admin")
    @description_md(
        """
        - **前提条件**: guestで通知を1件作成した後、ログアウトしてadminでログインし直した
        - **テスト手順**: 1. adminで通知一覧画面を表示する
        - **期待する結果**: guestで作成した通知はadminの一覧に表示されない（アカウントごとにデータが独立している）
        """
    )
    def test_gd028_02_guest_notification_is_not_visible_to_admin(
        self, app: SupportApp, credentials
    ) -> None:
        title = "GUEST" + app.notifications.random_chars(8)
        app.login.login(credentials.guest_id, credentials.guest_password)
        app.header.open_tab("通知")
        app.notifications.open_create_modal()
        app.notifications.fill_form(title, "guest-only")
        app.notifications.submit()
        app.header.open_user_menu()
        app.header.click_logout()
        app.login.login(credentials.admin_id, credentials.admin_password)
        app.header.open_tab("通知")
        assert title not in app.notifications.titles(), "Guest notification is visible to admin"
        _passed("The guest notification is absent from the admin list")

    # Step 1 bỏ trống thì nút 次へ của drawer vẫn disable.
    @allure.title("Testcases_028: GD02.8-03 Next stays disabled when step 1 is empty")
    @description_md(
        """
        - **前提条件**: ドロワーのStep1を表示中
        - **テスト手順**: 1. 件名・優先度・担当者を未入力のままにする
        - **期待する結果**: 「次へ」ボタンが非活性のままである
        """
    )
    def test_gd028_03_drawer_next_stays_disabled_when_required_fields_empty(
        self, admin_app: SupportApp
    ) -> None:
        admin_app.tickets.click_toolbar_create()
        admin_app.drawer.expect_next_disabled()
        _passed("Next stays disabled while step 1 is empty")

    # Guest đăng nhập thì header hiện tên guest.
    @allure.title("Testcases_029: GD02.3-004 guest login shows the guest name")
    @description_md(
        """
        - **前提条件**: ログイン画面を表示中
        - **テスト手順**: 1. IDに「guest」を入力する
          2. パスワードに「guest123」を入力する
          3. 「ログイン」ボタンを押下する
        - **期待する結果**: ログインでき、ヘッダーに「鈴木 花子（新規ユーザー）」と表示される
        """
    )
    def test_gd023_004_guest_login_shows_guest_name_in_header(
        self, app: SupportApp, credentials
    ) -> None:
        app.login.login(credentials.guest_id, credentials.guest_password)
        app.header.expect_username(messages.GUEST_HEADER_NAME)
        _passed("Guest login shows 鈴木 花子（新規ユーザー）")

    # Hover icon trợ giúp ở cột 作成日 thì hiện tooltip.
    @allure.title("Testcases_030: GD02.5-001 created-date help shows the tooltip")
    @description_md(
        """
        - **前提条件**: チケット一覧画面を表示中
        - **テスト手順**: 1. 「作成日」列見出し横のヘルプアイコン（?）にカーソルを合わせる
        - **期待する結果**: 「チケットが作成された日付を表示します」という説明テキストが表示される
        """
    )
    def test_gd025_001_created_date_help_icon_shows_tooltip(
        self, admin_app: SupportApp
    ) -> None:
        admin_app.tickets.hover_created_help()
        admin_app.tickets.expect_created_tooltip(messages.CREATED_DATE_TOOLTIP)
        _passed("The created-date help icon shows its tooltip")

    # Token hết hạn: trang không có token nên không tự động hóa được.
    @allure.title("Testcases_031: Others_04 expired token blocks further actions")
    @description_md(
        """
        - **前提条件**: ログイン済み・正常に画面を表示している
        - **テスト手順**: 1. ログイン後、トークンの実際の有効期限が切れるまで待機する
          2. 有効期限切れ後に画面上で操作を行う
        - **期待する結果**:
          - トークン有効期限切れが検知されること
          - 仕様に従ったエラー表示またはログイン画面への遷移が発生すること
          - 不正なデータ操作が行われないこと
        """
    )
    def test_others_04_expired_token_blocks_further_actions(self) -> None:
        pytest.skip(
            "Spec incomplete for Others_04: the page has no authentication token and no "
            "expiry time. There is nothing to wait for, so token-expiry behavior cannot "
            "be automated."
        )

    # Đủ hơn 5 thông báo thì phân trang hiện và sang được trang 2.
    @allure.title("Testcases_032: GD02.1-10 notification pagination appears after 6 items")
    @description_md(
        """
        - **前提条件**: 通知を6件以上作成した状態
        - **テスト手順**: 1. 画面表示を確認する
          2. 「次へ」ボタンを押下する
        - **期待する結果**: ページネーションが表示され、2ページ目に切り替えられる
        """
    )
    def test_gd021_10_notification_pagination_appears_when_more_than_five(
        self, admin_app: SupportApp
    ) -> None:
        admin_app.header.open_tab("通知")
        for index in range(3):
            admin_app.notifications.ensure_notification_exists(
                f"PAGE{index}" + admin_app.notifications.random_chars(6),
                "pagination-setup",
            )
        admin_app.notifications.expect_pagination_visible()
        admin_app.notifications.click_next()
        admin_app.notifications.expect_page_selected(2)
        _passed("Notification pagination opens page 2")

    # Tạo ticket xong thì drawer đóng, dòng mới ở trạng thái 未対応, có toast.
    @allure.title("Testcases_033: GD02.1-11 creating a ticket adds an untreated row")
    @description_md(
        """
        - **前提条件**: ドロワーのStep2を表示中
        - **テスト手順**: 1. 「作成する」ボタンを押下する
        - **期待する結果**: ドロワーが閉じ、一覧の先頭に新しいチケット（ステータス：未対応）が追加され、トースト通知が表示される
        """
    )
    def test_gd021_11_drawer_submit_adds_untreated_ticket_and_toast(
        self, admin_app: SupportApp
    ) -> None:
        subject = "AUTO" + admin_app.drawer.random_chars(8)
        admin_app.tickets.click_toolbar_create()
        admin_app.drawer.fill_step1(subject, messages.PRIORITY_HIGH, "佐藤")
        admin_app.drawer.click_next()
        admin_app.drawer.click_create()
        admin_app.drawer.expect_closed()
        assert admin_app.tickets.subjects()[0] == subject, "New ticket is not first"
        assert admin_app.tickets.status_of(subject) == messages.STATUS_UNTREATED, (
            "New ticket status is not 未対応"
        )
        admin_app.tickets.expect_toast(messages.TICKET_CREATED_TOAST)
        _passed("The new untreated ticket is first and a toast is shown")

    # Tab manual bên ngoài mở đúng trang hướng dẫn.
    @allure.title("Testcases_034: GD03.3-03 external manual tab shows the manual site")
    @description_md(
        """
        - **前提条件**: チケット一覧画面を表示中・インターネット接続あり
        - **テスト手順**: 1. 「外部マニュアルを開く（新しいタブ）」を押下する
          2. 実際の外部サイトを操作する
          3. ページ表示・リンク・画像等を確認する
        - **期待する結果**: 外部サイトが正常に表示され、想定されたコンテンツを閲覧できる
        """
    )
    def test_gd033_03_external_manual_tab_shows_the_manual_site(
        self, admin_app: SupportApp
    ) -> None:
        popup = admin_app.tickets.open_manual()
        try:
            admin_app.tickets.expect_manual_loaded(popup)
            admin_app.tickets.open_manual_section(popup)
        finally:
            popup.close()
        _passed("The manual site loads and a documentation link can be opened")

    # Checkbox chọn tất cả check đúng input của các dòng đang hiện.
    @allure.title("Testcases_035: GD02.2-001 header checkbox selects every visible row")
    @description_md(
        """
        - **前提条件**: チケット一覧画面を表示中
        - **テスト手順**: 1. テーブルヘッダーの全選択チェックボックスを押下する
        - **期待する結果**: 表示中の全行のチェックボックスがチェックされ、一括操作バーが表示される
        """
    )
    def test_gd022_001_header_checkbox_selects_all_visible_rows(
        self, admin_app: SupportApp
    ) -> None:
        admin_app.tickets.check_select_all()
        admin_app.tickets.expect_all_visible_rows_checked()
        admin_app.tickets.expect_bulk_bar_visible()
        _passed("Select-all checks every visible row and shows the bulk bar")

    # Bấm 作成する hai lần liên tiếp thì không được tạo trùng.
    @allure.title("Testcases_036: GD02.1-12 rapid create clicks do not duplicate a ticket")
    @description_md(
        """
        - **前提条件**: 通知作成またはチケット作成画面を表示中
        - **テスト手順**: 1. 「作成する」ボタンを短時間に連続して押下する
          2. 一覧とトースト通知を確認する
        - **期待する結果**: 同一データが二重登録されず、ボタンの非活性化など仕様に沿って二重送信が防止される
        """
    )
    def test_gd021_12_rapid_create_clicks_do_not_duplicate_the_ticket(
        self, admin_app: SupportApp
    ) -> None:
        subject = "AUTO" + admin_app.drawer.random_chars(8)
        admin_app.tickets.click_toolbar_create()
        admin_app.drawer.fill_step1(subject, messages.PRIORITY_HIGH, "佐藤")
        admin_app.drawer.click_next()
        admin_app.drawer.click_create_twice()
        admin_app.tickets.set_per_page("50")
        assert admin_app.tickets.count_subject(subject) == 1, "Ticket was registered twice"
        _passed("Two rapid create clicks register the ticket once")

    # Đăng xuất thì về màn login.
    @allure.title("Testcases_037: GD02.1-13 logout returns to the login screen")
    @description_md(
        """
        - **前提条件**: ユーザーメニューを表示中
        - **テスト手順**: 1. 「ログアウト」を押下する
        - **期待する結果**: ログイン画面に戻り、メイン画面が表示されなくなる
        """
    )
    def test_gd021_13_logout_returns_to_login_screen(self, admin_app: SupportApp) -> None:
        admin_app.header.open_user_menu()
        admin_app.header.click_logout()
        admin_app.login.expect_login_screen()
        admin_app.login.expect_main_hidden()
        _passed("Logout returns to the login screen")

    # Check một dòng thì thanh thao tác hàng loạt hiện, bỏ check thì ẩn.
    @allure.title("Testcases_038: GD02.2-002 bulk bar follows the row checkbox")
    @description_md(
        """
        - **前提条件**: チケット一覧画面を表示中
        - **テスト手順**: 1. 行のチェックボックスを1件チェックする
          2. 同じチェックボックスのチェックを外す
        - **期待する結果**: チェック時に一括操作バーが表示され、チェックを外すと非表示になる
        """
    )
    def test_gd022_002_bulk_bar_follows_row_checkbox(self, admin_app: SupportApp) -> None:
        subject = admin_app.tickets.subjects()[0]
        admin_app.tickets.check_row(subject)
        admin_app.tickets.expect_bulk_bar_visible()
        admin_app.tickets.uncheck_row(subject)
        admin_app.tickets.expect_bulk_bar_hidden()
        _passed("The bulk bar appears and disappears with the row checkbox")

    # Upload png qua input ẩn, hiện tên, dung lượng và nút xóa file.
    @allure.title("Testcases_039: GD02.7-01 png upload shows name, size, and remove")
    @description_md(
        """
        - **前提条件**: 詳細ダイアログを表示中
        - **テスト手順**: 1. ドロップゾーンに.pngファイル（1MB程度）をアップロードする
        - **期待する結果**: ファイル名とサイズがプレビュー表示され、削除アイコンが表示される
        """
    )
    def test_gd027_01_png_upload_shows_name_size_and_remove_icon(
        self, admin_app: SupportApp
    ) -> None:
        path = write_sample(".png", 1024 * 1024)
        try:
            admin_app.tickets.open_detail(admin_app.tickets.subjects()[0])
            admin_app.detail.upload(path)
            label = f"sample.png（{math.ceil(path.stat().st_size / 1024)}KB）"
            admin_app.detail.expect_file_preview(label)
        finally:
            shutil.rmtree(path.parent, ignore_errors=True)
        _passed("The png preview shows the file name, size, and remove icon")

    # Chặn host manual thì app không crash.
    @allure.title("Testcases_040: Others_05 a failed manual link does not crash the app")
    @description_md(
        """
        - **前提条件**: 外部マニュアルへのリンクが設定されている
        - **テスト手順**: 1. 外部サイトが一時的に利用できない状態でリンクを押下する
          2. 表示内容を確認する
        - **期待する結果**: 外部サイト障害時でもアプリ側がクラッシュせず、ブラウザ側で適切にエラーが表示される
        """
    )
    def test_others_05_manual_link_failure_does_not_crash_the_app(
        self, admin_app: SupportApp
    ) -> None:
        errors = admin_app.tickets.track_page_errors()
        admin_app.tickets.block_manual_host()
        popup = admin_app.tickets.open_manual()
        try:
            admin_app.tickets.expect_browser_error_page(popup)
        finally:
            popup.close()
        admin_app.tickets.expect_list_visible()
        assert not errors, "The app crashed when the manual host failed"
        _passed("A failed manual link shows a browser error and the app stays open")

    # Tìm ログイン thì chỉ còn một ticket.
    @allure.title("Testcases_041: GD02.3-005 search for ログイン shows one ticket")
    @description_md(
        """
        - **前提条件**: チケット一覧画面を表示中
        - **テスト手順**: 1. 検索欄に「ログイン」と入力する
          2. 「検索」ボタンを押下する
        - **期待する結果**: 件名または担当者に「ログイン」を含むチケットのみ表示される（1件）
        """
    )
    def test_gd023_005_search_login_shows_one_ticket(self, admin_app: SupportApp) -> None:
        admin_app.tickets.search(messages.SEARCH_KEYWORD)
        subjects = admin_app.tickets.subjects()
        assert len(subjects) == 1, "Login search did not return 1 ticket"
        assert messages.SEARCH_KEYWORD in subjects[0], "The row does not contain ログイン"
        _passed("Search for ログイン returns one matching ticket")

    # Hủy hoàn thành hàng loạt thì trạng thái và lựa chọn giữ nguyên.
    @allure.title("Testcases_042: GD03.1-04 bulk-complete cancel keeps status and selection")
    @description_md(
        """
        - **前提条件**: 一括対応完了の確認ダイアログを表示中
        - **テスト手順**: 1. 確認ダイアログで「キャンセル」を押下する
        - **期待する結果**: ステータスは変更されず、選択状態が維持される
        """
    )
    def test_gd031_04_bulk_complete_cancel_keeps_status_and_selection(
        self, admin_app: SupportApp
    ) -> None:
        subjects = admin_app.tickets.subjects()[:2]
        before = {subject: admin_app.tickets.status_of(subject) for subject in subjects}
        for subject in subjects:
            admin_app.tickets.check_row(subject)
        admin_app.tickets.bulk_complete(accept=False)
        for subject, status in before.items():
            assert admin_app.tickets.status_of(subject) == status, "Status changed after cancel"
            admin_app.tickets.expect_row_checked(subject)
        admin_app.tickets.expect_bulk_bar_visible()
        _passed("Cancelling bulk complete keeps status and selection")

    # Bàn phím thao tác được ô tìm kiếm và checkbox.
    @allure.title("Testcases_043: GD02.6-01 keyboard operates search and a checkbox")
    @description_md(
        """
        - **前提条件**: ログイン済み・チケット一覧画面を表示中
        - **テスト手順**: 1. マウスを使用せず、Tab・Shift+Tab・Enter・Space等で主要操作を行う
          2. フォーカス位置を確認する
        - **期待する結果**: 主要な操作要素へ適切な順序でフォーカスが移動し、キーボードだけで操作できる
        """
    )
    def test_gd026_01_keyboard_operates_search_and_checkbox(
        self, admin_app: SupportApp
    ) -> None:
        admin_app.tickets.focus_search()
        admin_app.tickets.press_tab()
        assert admin_app.tickets.focused_name() == "検索", "Tab did not move to the search button"
        admin_app.tickets.press_shift_tab()
        assert admin_app.tickets.focused_name() != "検索", "Shift+Tab did not leave the search button"
        admin_app.tickets.focus_search()
        admin_app.tickets.fill_search(messages.SEARCH_KEYWORD)
        admin_app.tickets.press_enter_in_search()
        assert admin_app.tickets.visible_row_count() == 1, "Enter did not run the search"
        admin_app.tickets.space_on_first_checkbox()
        admin_app.tickets.expect_first_checkbox_checked()
        _passed("Tab, Shift+Tab, Enter, and Space operate the main controls")

    # Sai mật khẩu thì báo lỗi và ở lại màn login.
    @allure.title("Testcases_044: GD02.8-04 wrong password shows an error and stays")
    @description_md(
        """
        - **前提条件**: ログイン画面を表示中
        - **テスト手順**: 1. IDに「admin」を入力する
          2. パスワードに「wrongpass」を入力する
          3. 「ログイン」ボタンを押下する
        - **期待する結果**: 「IDまたはパスワードが正しくありません。」というエラーメッセージが表示され、画面遷移しない
        """
    )
    def test_gd028_04_wrong_password_shows_error_and_stays_on_login(
        self, app: SupportApp, credentials
    ) -> None:
        app.login.fill_id(credentials.admin_id)
        app.login.fill_password(messages.WRONG_PASSWORD)
        app.login.submit()
        app.login.expect_error(messages.LOGIN_ERROR)
        app.login.expect_main_hidden()
        app.login.expect_login_screen()
        _passed("A wrong password shows the error and stays on login")

    # Bấm 次へ ở drawer thì step 2 hiện đúng giá trị đã nhập.
    @allure.title("Testcases_045: GD02.3-006 Next shows the entered values on step 2")
    @description_md(
        """
        - **前提条件**: ドロワーのStep1を表示中
        - **テスト手順**: 1. 件名・優先度・担当者を入力する
          2. 「次へ」ボタンを押下する
        - **期待する結果**: Step2（確認）に遷移し、入力した内容が確認画面に表示される
        """
    )
    def test_gd023_006_drawer_next_shows_entered_values_on_step2(
        self, admin_app: SupportApp
    ) -> None:
        subject = "AUTO" + admin_app.drawer.random_chars(6)
        admin_app.tickets.click_toolbar_create()
        admin_app.drawer.fill_step1(subject, "中", "鈴木")
        admin_app.drawer.click_next()
        admin_app.drawer.expect_step2(subject, "中", "鈴木")
        _passed("Step 2 shows the subject, priority, and assignee")

    # Hủy hộp thoại file của OS: input đang ẩn nên không tự động hóa được.
    @allure.title("Testcases_046: GD02.7-02 cancelling the OS file dialog changes nothing")
    @description_md(
        """
        - **前提条件**: ファイルアップロード画面を表示中
        - **テスト手順**: 1. ファイルアップロード領域を押下する
          2. OSのファイル選択ダイアログを表示する
          3. ダイアログをキャンセルして画面に戻る
        - **期待する結果**: ファイルは選択されず、画面の入力状態や既存ファイルが意図せず変更されない
        """
    )
    def test_gd027_02_file_dialog_cancel_keeps_existing_files(self) -> None:
        pytest.skip(
            "Spec incomplete for GD02.7-02: the file input is display:none and Playwright "
            "cannot cancel the OS file dialog. The project rules require set_input_files, "
            "so this cancel path cannot be automated reliably."
        )

    # Thiếu trường bắt buộc thì nút tạo thông báo vẫn disable.
    @allure.title("Testcases_047: GD02.8-05 notification Create stays disabled")
    @description_md(
        """
        - **前提条件**: 通知作成モーダルを表示中
        - **テスト手順**: 1. タイトルまたは内容を未入力のままにする
        - **期待する結果**: 「作成する」ボタンが非活性のままである
        """
    )
    def test_gd028_05_notification_submit_stays_disabled_when_required_empty(
        self, admin_app: SupportApp
    ) -> None:
        admin_app.header.open_tab("通知")
        admin_app.notifications.open_create_modal()
        admin_app.notifications.fill_form("タイトルのみ", "")
        admin_app.notifications.expect_submit_disabled()
        _passed("Create stays disabled when the content is empty")

    # Timeout phiên: trang không định nghĩa thời gian timeout.
    @allure.title("Testcases_048: Others_06 idle session follows the timeout specification")
    @description_md(
        """
        - **前提条件**: ログイン済み・ログイン状態を維持している
        - **テスト手順**: 1. 画面を操作せず、仕様上のセッションタイムアウト時間まで待機する
          2. その後、画面上の操作を行う
        - **期待する結果**: 仕様に従ってセッションが維持される、またはセッション切れとして適切に処理される
        """
    )
    def test_others_06_idle_session_follows_timeout_spec(self) -> None:
        pytest.skip(
            "Spec incomplete for Others_06: the page does not define or implement a session "
            "timeout. Waiting for an unknown timeout cannot be automated reliably."
        )

    # Bấm 戻る thì dữ liệu step 1 vẫn còn.
    @allure.title("Testcases_049: GD02.1-14 Back keeps the step 1 input")
    @description_md(
        """
        - **前提条件**: ドロワーのStep2を表示中
        - **テスト手順**: 1. 「戻る」ボタンを押下する
        - **期待する結果**: Step1に戻り、入力済みの内容が保持されている
        """
    )
    def test_gd021_14_drawer_back_keeps_step1_input(self, admin_app: SupportApp) -> None:
        subject = "AUTO" + admin_app.drawer.random_chars(6)
        admin_app.tickets.click_toolbar_create()
        admin_app.drawer.fill_step1(subject, "低", "高橋")
        admin_app.drawer.click_next()
        admin_app.drawer.click_back()
        admin_app.drawer.expect_step1_visible()
        assert admin_app.drawer.step1_values() == (subject, "低", "高橋"), (
            "Step 1 did not keep the entered values"
        )
        _passed("Back returns to step 1 with the entered values")

    # Chưa nhập mật khẩu thì nút login vẫn disable.
    @allure.title("Testcases_050: GD02.8-06 login stays disabled when password is empty")
    @description_md(
        """
        - **前提条件**: ログイン画面を表示中
        - **テスト手順**: 1. IDに「admin」を入力する
          2. パスワードは未入力のままにする
        - **期待する結果**: 「ログイン」ボタンが非活性のままである
        """
    )
    def test_gd028_06_login_stays_disabled_when_password_empty(
        self, app: SupportApp, credentials
    ) -> None:
        app.login.fill_id(credentials.admin_id)
        app.login.expect_login_disabled()
        _passed("Login stays disabled when the password is empty")

    # Guest không có ticket và phân trang bị ẩn, không phải disable.
    @allure.title("Testcases_051: GD02.8-07 guest ticket list is empty without pagination")
    @description_md(
        """
        - **前提条件**: guestでログイン済み
        - **テスト手順**: 1. チケット一覧画面の表示を確認する
        - **期待する結果**: チケットが0件で「登録されているチケットはありません。」というメッセージと「＋新規チケット作成」ボタンが表示される。ページネーションは表示されない
        """
    )
    def test_gd028_07_guest_ticket_list_is_empty_without_pagination(
        self, guest_app: SupportApp
    ) -> None:
        assert guest_app.tickets.visible_row_count() == 0, "Guest ticket list is not empty"
        guest_app.tickets.expect_message(messages.EMPTY_TICKETS)
        guest_app.tickets.expect_empty_create_visible()
        guest_app.tickets.expect_pagination_hidden()
        _passed("Guest tickets are empty, with the create button and no pagination")

    # Phóng to trình duyệt thì các control chính vẫn dùng được.
    @allure.title("Testcases_052: Others_07 browser zoom keeps the main UI usable")
    @description_md(
        """
        - **前提条件**: チケット一覧画面を表示中
        - **テスト手順**: 1. ブラウザのズーム倍率を変更する
          2. ヘッダー・一覧・ダイアログ・ドロワー等を確認する
        - **期待する結果**: 主要なUIが重なったり画面外にはみ出したりせず、仕様上許容される範囲で表示される
        """
    )
    def test_others_07_browser_zoom_keeps_main_ui_usable(self, admin_app: SupportApp) -> None:
        for zoom in ("150%", "80%"):
            admin_app.tickets.set_zoom(zoom)
            admin_app.tickets.expect_main_controls_fit()
            admin_app.tickets.click_toolbar_create()
            admin_app.drawer.expect_open_on_step1()
            admin_app.drawer.click_cancel()
            admin_app.tickets.open_detail(admin_app.tickets.subjects()[0])
            admin_app.detail.expect_open()
            admin_app.detail.click_close()
        _passed("Header, list, drawer, and detail stay usable at 150% and 80% zoom")

    # Popup in có nội dung ticket để in.
    @allure.title("Testcases_053: Others_08 print preview can start a print")
    @description_md(
        """
        - **前提条件**: 印刷プレビューを開ける状態
        - **テスト手順**: 1. 「印刷プレビューを開く（新しいウィンドウ）」を押下する
          2. 実ブラウザの印刷操作を実行する
          3. 印刷ダイアログの表示内容を確認する
        - **期待する結果**: 印刷対象の内容が正しく表示され、印刷操作に必要な項目が正常に表示される
        """
    )
    def test_others_08_print_preview_exposes_printable_ticket_content(
        self, admin_app: SupportApp
    ) -> None:
        admin_app.tickets.set_per_page("50")
        count = admin_app.tickets.visible_row_count()
        popup = admin_app.tickets.open_print_preview()
        try:
            admin_app.tickets.expect_print_preview(popup, count)
            assert admin_app.tickets.print_preview(popup), "The print event did not fire"
        finally:
            popup.close()
        _passed("Print preview shows the ticket count and accepts a print request")

    # Đóng dialog chi tiết thì phần sửa 件名 bị hủy.
    @allure.title("Testcases_054: GD02.1-15 closing detail discards the subject edit")
    @description_md(
        """
        - **前提条件**: 詳細ダイアログを表示中
        - **テスト手順**: 1. 件名を変更する
          2. 「閉じる」ボタンを押下する
          3. 再度同じ行の「詳細」ボタンを押下する
        - **期待する結果**: 変更前の件名が表示され、編集内容は保存されていない
        """
    )
    def test_gd021_15_detail_close_discards_subject_edits(
        self, admin_app: SupportApp
    ) -> None:
        subject = admin_app.tickets.subjects()[0]
        admin_app.tickets.open_detail(subject)
        admin_app.detail.fill_subject(subject + "変更")
        admin_app.detail.click_close()
        admin_app.tickets.open_detail(subject)
        assert admin_app.detail.subject_value() == subject, "Closing detail saved the subject"
        _passed("Closing detail discards the subject edit")

    # Chọn 完了にする trong kebab thì trạng thái đổi và có toast.
    @allure.title("Testcases_055: GD02.1-16 kebab complete updates the status")
    @description_md(
        """
        - **前提条件**: チケット一覧画面を表示中
        - **テスト手順**: 1. 任意の行の「⋮」ボタンを押下する
          2. 表示されたメニューから「完了にする」を選択する
        - **期待する結果**: メニューが閉じ、該当行のステータスが「完了」に変わる。トースト通知が表示される
        """
    )
    def test_gd021_16_kebab_complete_updates_status_and_shows_toast(
        self, admin_app: SupportApp
    ) -> None:
        subject = admin_app.tickets.subjects()[0]
        admin_app.tickets.open_kebab(subject)
        admin_app.tickets.choose_complete(subject)
        admin_app.tickets.expect_kebab_closed(subject)
        assert admin_app.tickets.status_of(subject) == messages.STATUS_DONE, (
            "Status did not become 完了"
        )
        admin_app.tickets.expect_toast(messages.STATUS_TOAST)
        _passed("Kebab complete sets the status to 完了 and shows a toast")

    # Năm thông báo trở xuống thì phân trang bị ẩn.
    @allure.title("Testcases_056: GD02.8-08 notification pagination is hidden for 5 or fewer")
    @description_md(
        """
        - **前提条件**: 通知が5件以下の状態
        - **テスト手順**: 1. 画面表示を確認する
        - **期待する結果**: ページネーション（前へ/次へ/ページ番号）が表示されない
        """
    )
    def test_gd028_08_notification_pagination_hidden_when_five_or_fewer(
        self, admin_app: SupportApp
    ) -> None:
        admin_app.header.open_tab("通知")
        assert len(admin_app.notifications.titles()) <= 5, "The default list already has more than 5"
        admin_app.notifications.expect_pagination_hidden()
        _passed("Notification pagination is hidden when there are 5 or fewer")

    # Đổi bộ lọc ưu tiên thì checkbox đang chọn bị bỏ và thanh hàng loạt ẩn.
    @allure.title("Testcases_057: GD02.4-03 changing priority clears the selection")
    @description_md(
        """
        - **前提条件**: 行を1件チェック済み（一括操作バー表示中）
        - **テスト手順**: 1. 優先度プルダウンの値を変更する
        - **期待する結果**: チェックしていた行の選択状態が解除され、一括操作バーが非表示になる
        """
    )
    def test_gd024_03_priority_change_clears_row_selection(
        self, admin_app: SupportApp
    ) -> None:
        admin_app.tickets.check_row(admin_app.tickets.subjects()[0])
        admin_app.tickets.expect_bulk_bar_visible()
        admin_app.tickets.select_priority(messages.PRIORITY_HIGH)
        admin_app.tickets.expect_no_checked_rows()
        admin_app.tickets.expect_bulk_bar_hidden()
        _passed("Changing priority clears the selection and hides the bulk bar")

    # Có mạng trở lại thì tìm kiếm chạy lại được.
    @allure.title("Testcases_058: Others_09 actions work again after the network returns")
    @description_md(
        """
        - **前提条件**: 通信エラーが発生している状態
        - **テスト手順**: 1. 実ネットワーク接続を復旧する
          2. 失敗した操作を再度実行する
        - **期待する結果**: ネットワーク復旧後、正常に通信が再開され、データが正しく表示・更新される
        """
    )
    def test_others_09_actions_work_again_after_network_returns(
        self, admin_app: SupportApp
    ) -> None:
        admin_app.tickets.set_offline(True)
        admin_app.tickets.search(messages.SEARCH_KEYWORD)
        admin_app.tickets.set_offline(False)
        admin_app.tickets.search(messages.SEARCH_KEYWORD)
        subjects = admin_app.tickets.subjects()
        assert len(subjects) == 1, "Search did not return data after reconnecting"
        assert messages.SEARCH_KEYWORD in subjects[0], "The restored row does not match ログイン"
        _passed("Search returns the matching ticket after the network returns")

    # File quá 5MB thì báo lỗi dung lượng và không có preview.
    @allure.title("Testcases_059: GD02.7-03 an oversize file shows the size error")
    @description_md(
        """
        - **前提条件**: 詳細ダイアログを表示中
        - **テスト手順**: 1. ドロップゾーンに5MBを超えるファイルをアップロードする
        - **期待する結果**: 「ファイルサイズが大きすぎます。」というエラーが表示され、プレビューされない
        """
    )
    def test_gd027_03_oversize_file_shows_size_error_without_preview(
        self, admin_app: SupportApp
    ) -> None:
        path = write_sample(".png", 5 * 1024 * 1024 + 1)
        try:
            admin_app.tickets.open_detail(admin_app.tickets.subjects()[0])
            admin_app.detail.upload(path)
            admin_app.detail.expect_file_error(messages.FILE_SIZE_ERROR)
            admin_app.detail.expect_no_preview()
        finally:
            shutil.rmtree(path.parent, ignore_errors=True)
        _passed("An oversize file shows the size error and no preview")

    # Lưu cài đặt thì có toast.
    @allure.title("Testcases_060: GD02.1-17 saving settings shows the toast")
    @description_md(
        """
        - **前提条件**: 設定画面を表示中
        - **テスト手順**: 1. 通知トグルを切り替える
          2. 「保存する」ボタンを押下する
        - **期待する結果**: 「設定を保存しました。」というトースト通知が表示される
        """
    )
    def test_gd021_17_settings_save_shows_toast(self, admin_app: SupportApp) -> None:
        admin_app.header.open_tab("設定")
        admin_app.settings.toggle_notifications()
        admin_app.settings.save()
        admin_app.settings.expect_toast(messages.SETTINGS_SAVED_TOAST)
        _passed("Saving settings shows 設定を保存しました。")

    # Bỏ trống cả ID và mật khẩu thì nút login vẫn disable.
    @allure.title("Testcases_061: GD02.8-09 login stays disabled when both fields are empty")
    @description_md(
        """
        - **前提条件**: ログイン画面を表示中
        - **テスト手順**: 1. IDとパスワードをどちらも未入力のままにする
        - **期待する結果**: 「ログイン」ボタンが非活性（disabled）のままである
        """
    )
    def test_gd028_09_login_stays_disabled_when_both_fields_empty(self, app: SupportApp) -> None:
        app.login.expect_login_disabled()
        _passed("Login is disabled when both fields are empty")

    # Xóa hết 件名 thì nút lưu chi tiết bị disable.
    @allure.title("Testcases_062: GD02.8-10 detail save is disabled when the subject is empty")
    @description_md(
        """
        - **前提条件**: 詳細ダイアログを表示中
        - **テスト手順**: 1. 「件名」を全て削除して空にする
        - **期待する結果**: 「保存する」ボタンが非活性になる
        """
    )
    def test_gd028_10_detail_save_disabled_when_subject_empty(
        self, admin_app: SupportApp
    ) -> None:
        admin_app.tickets.open_detail(admin_app.tickets.subjects()[0])
        admin_app.detail.fill_subject("")
        admin_app.detail.expect_save_disabled()
        _passed("Detail save is disabled when the subject is empty")

    # Tab thông báo của admin hiện 3 thông báo có sẵn.
    @allure.title("Testcases_063: GD01_004 notification tab shows 3 notifications")
    @description_md(
        """
        - **前提条件**: admin/admin123でログイン済み
        - **テスト手順**: 1. ヘッダーの「通知」タブを押下する
        - **期待する結果**: 通知一覧画面に遷移し、3件の通知が表示される
        """
    )
    def test_gd01_004_notification_tab_shows_three_notifications(
        self, admin_app: SupportApp
    ) -> None:
        admin_app.header.open_tab("通知")
        admin_app.notifications.expect_screen()
        assert len(admin_app.notifications.titles()) == 3, "The notification list does not show 3 items"
        _passed("The notification tab shows 3 notifications")

    # Áp dụng trạng thái trong iframe không đổi danh sách bên ngoài.
    @allure.title("Testcases_064: GD03.2-01 iframe apply does not change the parent list")
    @description_md(
        """
        - **前提条件**: チケット一覧画面を表示中
        - **テスト手順**: 1. 埋め込みプレビュー内のプルダウンでステータスを選択する
          2. 埋め込みプレビュー内の「適用」ボタンを押下する
        - **期待する結果**: iframe内にのみ結果メッセージが表示され、親ページの一覧には影響しない
        """
    )
    def test_gd032_01_iframe_apply_does_not_change_parent_list(
        self, admin_app: SupportApp
    ) -> None:
        before = admin_app.tickets.statuses()
        result = admin_app.tickets.apply_embedded_status(messages.STATUS_IN_PROGRESS)
        assert result == messages.IFRAME_RESULT.format(status=messages.STATUS_IN_PROGRESS), (
            "Iframe result text does not match"
        )
        assert admin_app.tickets.statuses() == before, "Iframe apply changed the parent list"
        _passed("The iframe result stays inside the frame")

    # Bấm logo không chuyển trang.
    @allure.title("Testcases_065: GD02.1-18 logo click does not navigate")
    @description_md(
        """
        - **前提条件**: ログイン済み・チケット一覧画面を表示中
        - **テスト手順**: 1. ヘッダー左上のロゴ（🎫 サポートチケット管理）を押下する
        - **期待する結果**: 画面遷移や特別な動作は発生しない
        """
    )
    def test_gd021_18_logo_click_does_not_navigate(self, admin_app: SupportApp) -> None:
        url = admin_app.page.url
        admin_app.header.click_logo()
        assert admin_app.page.url == url, "Logo click changed the URL"
        admin_app.tickets.expect_list_visible()
        admin_app.login.expect_main_visible()
        _passed("Logo click leaves the ticket list in place")

    # Admin đăng nhập thấy danh sách ticket và tên trên header.
    @allure.title("Testcases_066: GD02.3-007 admin login shows the ticket list and user name")
    @description_md(
        """
        - **前提条件**: ログイン画面を表示中
        - **テスト手順**: 1. IDに「admin」を入力する
          2. パスワードに「admin123」を入力する
          3. 「ログイン」ボタンを押下する
        - **期待する結果**: チケット一覧画面に遷移し、ヘッダーにログインユーザー名が表示される
        """
    )
    def test_gd023_007_admin_login_shows_ticket_list_and_user_name(
        self, app: SupportApp, credentials
    ) -> None:
        app.login.login(credentials.admin_id, credentials.admin_password)
        app.tickets.expect_list_visible()
        app.header.expect_username(messages.ADMIN_HEADER_NAME)
        _passed("Admin login shows the ticket list and 田中 太郎（管理者）")

    # Toast tự mất sau khoảng 3 giây.
    @allure.title("Testcases_067: GD02.8-11 toast disappears after about 3 seconds")
    @description_md(
        """
        - **前提条件**: いずれかの操作でトースト通知が表示された直後
        - **テスト手順**: 1. 何もせず数秒待つ
        - **期待する結果**: 約3秒後にトースト通知が自動的に消える
        """
    )
    def test_gd028_11_toast_disappears_after_about_three_seconds(
        self, admin_app: SupportApp
    ) -> None:
        admin_app.header.open_tab("設定")
        admin_app.settings.toggle_notifications()
        admin_app.settings.save()
        elapsed = admin_app.settings.seconds_until_toast_hides(messages.SETTINGS_SAVED_TOAST)
        assert 2.0 <= elapsed <= 6.0, "Toast did not disappear after about 3 seconds"
        _passed("The toast disappears about 3 seconds after it appears")

    # Thống kê chỉ cập nhật sau khi bấm 再集計する.
    @allure.title("Testcases_068: GD02.1-19 stats update only after recalculate")
    @description_md(
        """
        - **前提条件**: 統計画面を表示した後、チケット一覧画面で新規チケットを1件作成した
        - **テスト手順**: 1. 統計画面に戻る
          2. 件数が更新されていないことを確認する
          3. 「再集計する」ボタンを押下する
        - **期待する結果**: ボタン押下前は件数が作成前のままで、押下後に最新の件数へ更新される
        """
    )
    def test_gd021_19_stats_update_only_after_recalculate(self, admin_app: SupportApp) -> None:
        admin_app.header.open_tab("統計")
        before = admin_app.stats.counts()["total"]
        admin_app.header.open_tab("チケット一覧")
        subject = "AUTO" + admin_app.drawer.random_chars(6)
        admin_app.tickets.click_toolbar_create()
        admin_app.drawer.fill_step1(subject, messages.PRIORITY_HIGH, "田中")
        admin_app.drawer.click_next()
        admin_app.drawer.click_create()
        admin_app.header.open_tab("統計")
        assert admin_app.stats.counts()["total"] == before, "Stats changed before recalculate"
        admin_app.stats.recalculate()
        assert admin_app.stats.counts()["total"] == before + 1, "Recalculate did not add the ticket"
        _passed("Stats stay stale until recalculate, then include the new ticket")

    # Guest chưa có thông báo, có nút tạo mới và không có phân trang.
    @allure.title("Testcases_069: GD02.8-12 guest notifications are empty without pagination")
    @description_md(
        """
        - **前提条件**: guestでログイン済み
        - **テスト手順**: 1. 通知一覧画面の表示を確認する
        - **期待する結果**: 通知が0件で「通知はまだありません。」というメッセージと「＋通知を作成する」ボタンが表示される。ページネーションは表示されない
        """
    )
    def test_gd028_12_guest_notification_list_is_empty_without_pagination(
        self, guest_app: SupportApp
    ) -> None:
        guest_app.header.open_tab("通知")
        assert guest_app.notifications.titles() == [], "Guest notifications are not empty"
        guest_app.notifications.expect_text_visible(messages.EMPTY_NOTIFICATIONS)
        guest_app.notifications.expect_empty_create_visible()
        guest_app.notifications.expect_pagination_hidden()
        _passed("Guest notifications are empty, with the create button and no pagination")

    # Thống kê của guest toàn số 0.
    @allure.title("Testcases_070: GD02.8-13 guest statistics are all zero")
    @description_md(
        """
        - **前提条件**: guestでログイン済み
        - **テスト手順**: 1. 統計画面の表示を確認する
        - **期待する結果**: 合計チケット数・未対応・対応中・完了が全て0と表示される
        """
    )
    def test_gd028_13_guest_stats_are_all_zero(self, guest_app: SupportApp) -> None:
        guest_app.header.open_tab("統計")
        assert guest_app.stats.counts() == {
            "total": 0,
            "未対応": 0,
            "対応中": 0,
            "完了": 0,
        }, "Guest statistics are not all zero"
        _passed("Guest statistics are all zero")

    # Chip ưu tiên và trạng thái có màu khác nhau.
    @allure.title("Testcases_071: GD02.8-14 priority and status chips use different colors")
    @description_md(
        """
        - **前提条件**: チケット一覧画面を表示中
        - **テスト手順**: 1. 画面表示を確認する
        - **期待する結果**: 優先度・ステータスが色分けされたチップ（バッジ）で表示される
        """
    )
    def test_gd028_14_priority_and_status_chips_use_distinct_colors(
        self, admin_app: SupportApp
    ) -> None:
        admin_app.tickets.set_per_page("50")
        priorities = admin_app.tickets.chip_colors(("高", "中", "低"))
        statuses = admin_app.tickets.chip_colors(("未対応", "対応中", "完了"))
        assert len(set(priorities.values())) == 3, "Priority chips do not use distinct colors"
        assert len(set(statuses.values())) == 3, "Status chips do not use distinct colors"
        _passed("Priority and status chips use a distinct color for each value")

    # Upload file exe thì báo lỗi đuôi file và không có preview.
    @allure.title("Testcases_072: GD02.7-04 an exe upload shows the type error")
    @description_md(
        """
        - **前提条件**: 詳細ダイアログを表示中
        - **テスト手順**: 1. ドロップゾーンに.exeファイルをアップロードする
        - **期待する結果**: 「対応していないファイル形式です。」というエラーが表示され、プレビューされない
        """
    )
    def test_gd027_04_exe_upload_shows_extension_error_without_preview(
        self, admin_app: SupportApp
    ) -> None:
        path = write_sample(".exe", 128)
        try:
            admin_app.tickets.open_detail(admin_app.tickets.subjects()[0])
            admin_app.detail.upload(path)
            admin_app.detail.expect_file_error(messages.FILE_TYPE_ERROR)
            admin_app.detail.expect_no_preview()
        finally:
            shutil.rmtree(path.parent, ignore_errors=True)
        _passed("An exe file shows the type error and no preview")

    # Hoàn thành hàng loạt thì hiện hộp thoại xác nhận.
    @allure.title("Testcases_073: GD03.1-05 bulk complete opens a confirm dialog")
    @description_md(
        """
        - **前提条件**: 行を2件チェック済み
        - **テスト手順**: 1. 「選択した項目を一括対応完了にする」ボタンを押下する
        - **期待する結果**: ブラウザの確認ダイアログ（confirm）が表示される
        """
    )
    def test_gd031_05_bulk_complete_opens_confirm_dialog(self, admin_app: SupportApp) -> None:
        for subject in admin_app.tickets.subjects()[:2]:
            admin_app.tickets.check_row(subject)
        dialogs = admin_app.tickets.bulk_complete(accept=False)
        assert dialogs and dialogs[0][0] == "confirm", "Bulk complete did not open a confirm dialog"
        assert dialogs[0][1] == messages.BULK_CONFIRM.format(count=2), (
            "Bulk confirm message does not match"
        )
        _passed("Bulk complete opens the confirm dialog")

    # Manual mở ở tab mới.
    @allure.title("Testcases_074: GD03.3-04 external manual opens in a new tab")
    @description_md(
        """
        - **前提条件**: チケット一覧画面を表示中
        - **テスト手順**: 1. 「外部マニュアルを開く（新しいタブ）」ボタンを押下する
        - **期待する結果**: 新しいタブが開き、外部サイトが表示される
        """
    )
    def test_gd033_04_external_manual_opens_in_a_new_tab(self, admin_app: SupportApp) -> None:
        popup = admin_app.tickets.open_manual()
        try:
            admin_app.tickets.expect_manual_loaded(popup)
        finally:
            popup.close()
        _passed("The external manual opens in a new tab")

    # Hai user sửa cùng ticket: không có kho dữ liệu dùng chung.
    @allure.title("Testcases_075: Others_10 concurrent edits do not corrupt ticket data")
    @description_md(
        """
        - **前提条件**: 同一チケットを複数ユーザーが編集可能な状態
        - **テスト手順**: 1. ユーザーAとユーザーBが同一チケットを開く
          2. 両者が異なる内容を編集する
          3. ほぼ同時に保存する
        - **期待する結果**: 競合時の仕様に従って保存・エラー・上書き防止等が行われ、データが不整合にならない
        """
    )
    def test_others_10_concurrent_edits_do_not_corrupt_ticket_data(self) -> None:
        pytest.skip(
            "Spec incomplete for Others_10: ticket data is copied into each login and is "
            "not shared. Two users cannot open the same ticket, so a concurrent-edit "
            "conflict cannot be set up."
        )

    # Tắt trình duyệt từ OS sẽ làm chết runner nên không tự động hóa.
    @allure.title("Testcases_076: Others_11 the app recovers after a forced browser shutdown")
    @description_md(
        """
        - **前提条件**: 編集中または操作途中の画面を表示している
        - **テスト手順**: 1. ブラウザをOS操作で強制終了する
          2. ブラウザを再起動する
          3. アプリへ再アクセスする
        - **期待する結果**: アプリが正常に起動し、仕様に従ってセッションや未保存データが処理される
        """
    )
    def test_others_11_app_recovers_after_forced_browser_shutdown(self) -> None:
        pytest.skip(
            "Spec incomplete for Others_11: the case requires force-killing the browser "
            "from the OS. That would destroy the test runner, so recovery after a forced "
            "shutdown cannot be automated here."
        )

    # Dialog chi tiết hiện đúng ticket vừa chọn.
    @allure.title("Testcases_077: GD02.1-20 detail dialog shows the selected ticket")
    @description_md(
        """
        - **前提条件**: チケット一覧画面を表示中
        - **テスト手順**: 1. 任意の行の「詳細」ボタンを押下する
        - **期待する結果**: 該当チケットの件名・優先度・ステータス・担当者・作成日が入ったダイアログが表示される
        """
    )
    def test_gd021_20_detail_dialog_shows_the_selected_ticket(
        self, admin_app: SupportApp
    ) -> None:
        subject = admin_app.tickets.subjects()[0]
        fields = admin_app.tickets.row_fields(subject)
        admin_app.tickets.open_detail(subject)
        admin_app.detail.expect_open()
        admin_app.detail.expect_fields(
            fields["subject"],
            fields["priority"],
            fields["status"],
            fields["assignee"],
            fields["created"],
        )
        _passed("The detail dialog shows the selected ticket")

    # User kia cập nhật ticket đã xóa: không dựng được vì không có kho chung.
    @allure.title("Testcases_078: Others_12 another user cannot update a deleted ticket")
    @description_md(
        """
        - **前提条件**: 同一チケットを複数ユーザーが表示している
        - **テスト手順**: 1. ユーザーAで対象チケットを削除する
          2. ユーザーBで削除前から開いていた画面を操作する
        - **期待する結果**: 削除済みデータに対して不正な更新が行われず、仕様に従ったエラーまたは再取得が行われる
        """
    )
    def test_others_12_other_user_cannot_update_a_deleted_ticket(self) -> None:
        pytest.skip(
            "Spec incomplete for Others_12: there is no shared ticket store, so user B "
            "cannot be left on a ticket that user A deleted. The deleted-record conflict "
            "cannot be set up."
        )

    # Sang tab thống kê thì danh sách ticket bị ẩn.
    @allure.title("Testcases_079: GD01_005 stats tab hides the ticket list")
    @description_md(
        """
        - **前提条件**: ログイン済み
        - **テスト手順**: 1. ヘッダーの「統計」タブを押下する
        - **期待する結果**: 統計画面に遷移し、チケット一覧画面が非表示になる
        """
    )
    def test_gd01_005_stats_tab_hides_the_ticket_list(self, admin_app: SupportApp) -> None:
        admin_app.header.open_tab("統計")
        admin_app.stats.expect_screen()
        admin_app.tickets.expect_list_hidden()
        _passed("The stats tab hides the ticket list")

    # Cho máy sleep: runner không suspend được máy.
    @allure.title("Testcases_080: Others_13 session follows the specification after PC sleep")
    @description_md(
        """
        - **前提条件**: ログイン済み・画面を表示中
        - **テスト手順**: 1. PCをスリープ状態にする
          2. 一定時間後に復帰する
          3. アプリ画面を操作する
        - **期待する結果**: 復帰後も仕様に従ってセッションが維持または失効し、画面が正常に操作できる
        """
    )
    def test_others_13_session_survives_or_expires_after_pc_sleep(self) -> None:
        pytest.skip(
            "Spec incomplete for Others_13: the case requires putting the host PC to sleep. "
            "The test runner cannot suspend the machine, so post-sleep session behavior "
            "cannot be automated."
        )

    # Tab cài đặt mở đúng màn hình cài đặt.
    @allure.title("Testcases_081: GD01_006 settings tab opens the settings screen")
    @description_md(
        """
        - **前提条件**: ログイン済み
        - **テスト手順**: 1. ヘッダーの「設定」タブを押下する
        - **期待する結果**: 設定画面に遷移する
        """
    )
    def test_gd01_006_settings_tab_opens_settings_screen(self, admin_app: SupportApp) -> None:
        admin_app.header.open_tab("設定")
        admin_app.settings.expect_screen()
        _passed("The settings tab opens the settings screen")

    # Phím Enter tìm giống nút 検索.
    @allure.title("Testcases_082: GD02.6-02 Enter searches like the search button")
    @description_md(
        """
        - **前提条件**: チケット一覧画面を表示中
        - **テスト手順**: 1. 検索欄に「ログイン」と入力する
          2. Enterキーを押下する
        - **期待する結果**: 「検索」ボタン押下時と同じ結果が表示される
        """
    )
    def test_gd026_02_enter_key_searches_like_the_search_button(
        self, admin_app: SupportApp
    ) -> None:
        admin_app.tickets.search(messages.SEARCH_KEYWORD)
        by_button = admin_app.tickets.subjects()
        admin_app.tickets.search("")
        admin_app.tickets.fill_search(messages.SEARCH_KEYWORD)
        admin_app.tickets.press_enter_in_search()
        assert admin_app.tickets.subjects() == by_button, "Enter search differs from the button"
        _passed("Enter and the search button return the same rows")

    # Nút tạo ticket mới mở drawer ở step 1.
    @allure.title("Testcases_083: GD02.1-21 new ticket button opens step 1")
    @description_md(
        """
        - **前提条件**: チケット一覧画面を表示中
        - **テスト手順**: 1. 「＋新規チケット作成」ボタンを押下する
        - **期待する結果**: 画面右側からドロワーがスライド表示され、Step1（基本情報）が表示される
        """
    )
    def test_gd021_21_new_ticket_button_opens_step1_drawer(
        self, admin_app: SupportApp
    ) -> None:
        admin_app.tickets.click_toolbar_create()
        admin_app.drawer.expect_open_on_step1()
        _passed("The new-ticket button opens step 1 on the right")

    # Số trên thống kê khớp số liệu danh sách ticket.
    @allure.title("Testcases_084: GD02.8-15 statistics match the ticket list")
    @description_md(
        """
        - **前提条件**: 統計画面を表示中
        - **テスト手順**: 1. 「合計チケット数」「未対応」「対応中」「完了」の件数を確認する
        - **期待する結果**: チケット一覧画面のデータと一致した件数・グラフが表示される
        """
    )
    def test_gd028_15_stats_counts_match_the_ticket_list(self, admin_app: SupportApp) -> None:
        admin_app.tickets.set_per_page("50")
        statuses = admin_app.tickets.statuses()
        admin_app.header.open_tab("統計")
        counts = admin_app.stats.counts()
        assert counts["total"] == len(statuses), "Total does not match the ticket list"
        for status in ("未対応", "対応中", "完了"):
            assert counts[status] == statuses.count(status), f"{status} count does not match"
        total = counts["total"]
        bars = admin_app.stats.bar_percents()
        for status in ("未対応", "対応中", "完了"):
            expected = 0 if total == 0 else counts[status] / total * 100
            assert abs(bars[status] - expected) < 0.2, f"{status} bar does not match the count"
        _passed("Statistics counts and bars match the ticket list")

    # Cắt upload giữa chừng: upload chạy đồng bộ, không có request để ngắt.
    @allure.title("Testcases_085: Others_14 an interrupted upload does not commit partial data")
    @description_md(
        """
        - **前提条件**: 大容量ファイルのアップロードを実行中
        - **テスト手順**: 1. ファイルアップロードを開始する
          2. アップロード完了前にブラウザを終了する
          3. ブラウザを再起動してアプリへアクセスする
        - **期待する結果**: アップロード途中の状態が不正に確定されず、再アクセス後もデータ整合性が保たれる
        """
    )
    def test_others_14_interrupted_upload_does_not_commit_partial_data(self) -> None:
        pytest.skip(
            "Spec incomplete for Others_14: the upload handler finishes synchronously and "
            "there is no in-progress request to interrupt. Killing the browser would also "
            "destroy the runner, so partial-upload recovery cannot be automated."
        )

    # Chip loại thông báo có màu khác nhau.
    @allure.title("Testcases_086: GD02.8-16 notification type chips use different colors")
    @description_md(
        """
        - **前提条件**: 通知一覧画面を表示中
        - **テスト手順**: 1. 画面表示を確認する
        - **期待する結果**: 種別（お知らせ/警告/エラー）が色分けされたチップで表示される
        """
    )
    def test_gd028_16_notification_type_chips_use_distinct_colors(
        self, admin_app: SupportApp
    ) -> None:
        admin_app.header.open_tab("通知")
        colors = admin_app.notifications.chip_colors()
        assert len(set(colors.values())) == 3, "Notification type chips do not use distinct colors"
        _passed("Notice, warning, and error chips use distinct colors")

    # Tab 未対応 hiện 5 ticket.
    @allure.title("Testcases_087: GD02.1-22 untreated tab shows 5 tickets")
    @description_md(
        """
        - **前提条件**: チケット一覧画面を表示中
        - **テスト手順**: 1. ステータスタブ「未対応」を押下する
        - **期待する結果**: ステータスが「未対応」のチケットのみ表示される（5件）
        """
    )
    def test_gd021_22_untreated_tab_shows_five_tickets(self, admin_app: SupportApp) -> None:
        admin_app.tickets.select_status_tab(messages.STATUS_UNTREATED)
        statuses = admin_app.tickets.statuses()
        assert statuses == [messages.STATUS_UNTREATED] * 5, "Untreated filter is not 5 rows"
        _passed("The untreated tab shows 5 untreated tickets")

    # Xác nhận hoàn thành hàng loạt thì các dòng thành 完了 và có alert.
    @allure.title("Testcases_088: GD03.1-06 bulk complete OK sets status and alerts")
    @description_md(
        """
        - **前提条件**: 一括対応完了の確認ダイアログを表示中
        - **テスト手順**: 1. 確認ダイアログで「OK」を押下する
        - **期待する結果**: 選択した全件のステータスが「完了」に変わり、件数を通知するalertダイアログが表示される
        """
    )
    def test_gd031_06_bulk_complete_ok_sets_status_done_and_alerts(
        self, admin_app: SupportApp
    ) -> None:
        subjects = admin_app.tickets.subjects()[:2]
        for subject in subjects:
            admin_app.tickets.check_row(subject)
        dialogs = admin_app.tickets.bulk_complete(accept=True)
        assert [item[0] for item in dialogs] == ["confirm", "alert"], (
            "Bulk complete did not show confirm and then alert"
        )
        assert dialogs[1][1] == messages.BULK_ALERT.format(count=2), (
            "Alert does not report the completed count"
        )
        for subject in subjects:
            assert admin_app.tickets.status_of(subject) == messages.STATUS_DONE, (
                "Selected ticket did not become 完了"
            )
        _passed("Bulk complete marks both rows done and alerts the count")
