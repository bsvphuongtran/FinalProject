"""Locator catalog. One class per screen. Selectors stay out of tests and pages."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class By:
    """Resolver input for BasePage. `kind` is role, placeholder, text, label, or css."""

    kind: str
    value: str
    name: str | None = None
    exact: bool = True


def button_named(name: str) -> By:
    """ボタン名がデータ依存のときに使う。"""
    return By("role", "button", name=name, exact=True)


class LoginLocators:
    ID_INPUT = By("role", "textbox", name="ID")  # ID入力欄
    PASSWORD_INPUT = By("role", "textbox", name="パスワード")  # パスワード入力欄
    LOGIN_BUTTON = By("role", "button", name="ログイン", exact=True)  # ログインボタン
    LOGIN_HEADING = By("role", "heading", name="ログイン", exact=True)  # ログイン見出し
    LOGIN_SECTION = By("css", "#login_section")  # ログイン画面
    MAIN_SECTION = By("css", "#main_section")  # ログイン後のメイン画面
    LOGIN_ERROR = By("css", "#login_error")  # ログインエラー文


class HeaderLocators:
    LOGO = By("css", "#app_logo")  # ロゴはdivでroleがないためid
    NAV = By("css", "#nav_tabs")  # タブはhrefなしのli。roleが不安定なためコンテナidで限定
    USER_MENU_BUTTON = By("css", "#user_menu_activator")  # 表示名がアカウントで変わるためid
    USER_NAME = By("css", "#header_username")  # ヘッダーのユーザー名
    USER_MENU = By("css", "#user_menu_content")  # ユーザーメニュー
    SETTINGS_ITEM = By("role", "button", name="設定", exact=True)  # メニューの設定
    HELP_ITEM = By("role", "button", name="ヘルプ", exact=True)  # メニューのヘルプ
    LOGOUT_ITEM = By("role", "button", name="ログアウト", exact=True)  # ログアウト
    OUTSIDE = By("css", "#main_section")  # メニュー外のメイン領域


class TicketListLocators:
    PANEL = By("css", "#panel_tickets")  # チケット一覧パネル
    HEADING = By("role", "heading", name="チケット一覧", exact=True)  # チケット一覧の見出し
    CREATE_BUTTON = By("role", "button", name="新規チケット作成", exact=True)  # ツールバーの新規作成
    EMPTY_CREATE_BUTTON = By("role", "button", name="＋新規チケット作成", exact=True)  # 空状態の新規作成
    STATUS_FILTER = By("css", "#status_filter")  # ステータスタブ
    SEARCH_INPUT = By("role", "textbox", name="件名または担当者で検索", exact=True)  # チケット検索欄
    SEARCH_BUTTON = By("role", "button", name="検索", exact=True)  # 検索。通知側と同名なのでパネル内に限定
    PRIORITY_FILTER = By("role", "combobox", name="優先度で絞り込み", exact=True)  # 優先度プルダウン
    PER_PAGE = By("role", "combobox", name="表示件数", exact=True)  # 表示件数プルダウン
    PAGINATION_TOP = By("css", "#pagination_top")  # 上側のページネーション
    PAGINATION_BOTTOM = By("css", "#pagination_bottom")  # 下側のページネーション
    NEXT_BUTTON = By("role", "button", name="次へ", exact=True)  # 次へボタン
    PREV_BUTTON = By("role", "button", name="前へ", exact=True)  # 前へボタン
    TABLE_BODY = By("css", "#ticket_tbody")  # チケット表の本体
    TABLE_WRAP = By("css", "#panel_tickets .table-wrap")  # 表の横スクロール枠
    SELECT_ALL = By("role", "checkbox", name="全て選択", exact=True)  # 全選択チェックボックス
    CREATED_HEADER = By("css", "#th_created")  # 見出しinnerTextにソートiconとtooltipが混ざるためid
    SORT_ICON = By("css", "#sort_icon")  # ソートアイコン本体。見出し全文はassertしない
    CREATED_HELP = By("css", "#th_created .tooltip-wrap")  # ヘルプiconはaria-hiddenのためclass
    TOOLTIP = By("css", "#th_created .tooltip-content")  # 作成日のツールチップ
    BULK_BAR = By("css", "#bulk_action_bar")  # 一括操作バー
    BULK_COMPLETE = By(
        "role", "button", name="選択した項目を一括対応完了にする", exact=True
    )  # 一括対応完了ボタン
    DETAIL_BUTTON = By("role", "button", name="詳細", exact=True)  # 行の詳細ボタン
    DELETE_BUTTON = By("role", "button", name="削除", exact=True)  # 行の削除ボタン
    KEBAB_BUTTON = By("role", "button", name="その他の操作", exact=True)  # ケバブメニュー
    COMPLETE_ACTION = By("role", "button", name="完了にする", exact=True)  # 完了にする
    PRINT_PREVIEW = By(
        "role", "button", name="印刷プレビューを開く（新しいウィンドウ）", exact=True
    )  # 印刷プレビュー
    OPEN_MANUAL = By(
        "role", "button", name="外部マニュアルを開く（新しいタブ）", exact=True
    )  # 外部マニュアル
    REASSIGN = By("role", "button", name="担当者を再割り当てする", exact=True)  # 再割り当て
    REASSIGN_RESULT = By("css", "#reassign_result")  # 再割り当て結果
    CHECKED_ROWS = By("css", "#ticket_tbody input.row-checkbox:checked")  # 本物のinput。.cb-boxはクリックしない
    CHIP = By("css", "#ticket_tbody span.chip")  # チップにroleがないためclass


class TicketDetailLocators:
    OVERLAY = By("css", "#detail_overlay")  # チケット詳細ダイアログ
    TITLE = By("role", "heading", name="チケット詳細", exact=True)  # 詳細の見出し
    SUBJECT = By("label", "件名", exact=True)  # 詳細の件名。ドロワー側は「件名*」なのでexact
    PRIORITY = By("css", "#detail_priority")  # 詳細の優先度
    STATUS = By("css", "#detail_status")  # 詳細のステータス
    ASSIGNEE = By("css", "#detail_assignee")  # 詳細の担当者
    CREATED = By("css", "#detail_created")  # 詳細の作成日
    CLOSE_BUTTON = By("css", "#detail_close_btn")  # ダイアログ内の「閉じる」が2つあるためid
    SAVE_BUTTON = By("role", "button", name="保存する", exact=True)  # 詳細ダイアログ内に限定して使う
    FILE_INPUT = By("css", "#detail_file_input")  # display:none。set_input_files用。label未関連
    FILE_PREVIEW = By("css", "#detail_file_preview")  # ファイルプレビュー
    FILE_NAME = By("css", "#detail_file_name")  # ファイル名とサイズ
    REMOVE_FILE = By("role", "button", name="ファイルを削除", exact=True)  # ファイル削除アイコン
    FILE_ERROR = By("css", "#detail_file_error")  # ファイルエラー


class TicketDrawerLocators:
    DRAWER = By("css", "#ticket_drawer")  # 新規チケットドロワー
    TITLE = By("role", "heading", name="新規チケット作成", exact=True)  # ドロワーの見出し
    STEP1 = By("css", "#drawer_step1")  # Step1
    STEP2 = By("css", "#drawer_step2")  # Step2
    STEP1_INDICATOR = By("css", "#step_indicator_1")  # Step1インジケーター
    SUBJECT = By("placeholder", "例：ログインできない")  # 新規件名
    PRIORITY = By("label", "優先度", exact=False)  # ラベルは「優先度*」
    ASSIGNEE = By("label", "担当者", exact=False)  # ラベルは「担当者*」
    CANCEL = By("role", "button", name="キャンセル", exact=True)  # ドロワー内に限定して使う
    NEXT = By("css", "#drawer_next")  # 「次へ」はページ送りと重複し、閉じたドロワーもa11yに残るためid
    BACK = By("role", "button", name="戻る", exact=True)  # 戻る
    SUBMIT = By("role", "button", name="作成する", exact=True)  # Step2内。通知モーダルと同名
    CONFIRM_SUBJECT = By("css", "#confirm_subject")  # 確認の件名
    CONFIRM_PRIORITY = By("css", "#confirm_priority")  # 確認の優先度
    CONFIRM_ASSIGNEE = By("css", "#confirm_assignee")  # 確認の担当者


class NotificationLocators:
    PANEL = By("css", "#panel_notifications")  # 通知パネル
    HEADING = By("role", "heading", name="通知一覧", exact=True)  # 通知一覧の見出し
    CREATE_BUTTON = By("role", "button", name="通知を作成する", exact=True)  # ツールバーの作成
    EMPTY_CREATE = By("role", "button", name="＋通知を作成する", exact=True)  # 0件・検索0件の作成
    SEARCH_INPUT = By("role", "textbox", name="タイトルまたは内容で検索", exact=True)  # 通知検索欄
    SEARCH_BUTTON = By("role", "button", name="検索", exact=True)  # 検索。チケット側と同名なのでパネル内に限定
    TABLE_BODY = By("css", "#notification_tbody")  # 通知表の本体
    CHIP = By("css", "#notification_tbody span.chip")  # 種別チップ
    PAGINATION = By("css", "#notif_pagination")  # 通知のページネーション
    NEXT_BUTTON = By("role", "button", name="次へ", exact=True)  # 通知の次へ
    MODAL = By("css", "#notification_modal")  # 通知作成モーダル
    MODAL_TITLE = By("role", "heading", name="通知を作成", exact=True)  # モーダル見出し
    TITLE_INPUT = By("placeholder", "例：メンテナンスのお知らせ")  # タイトル入力
    CONTENT_INPUT = By("placeholder", "通知内容を入力")  # 内容入力
    SUBMIT = By("role", "button", name="作成する", exact=True)  # モーダル内に限定。ドロワーと同名


class StatsLocators:
    PANEL = By("css", "#panel_stats")  # 統計画面
    HEADING = By("role", "heading", name="統計", exact=True)  # 統計の見出し
    REFRESH = By("role", "button", name="再集計する", exact=True)  # 再集計ボタン
    TOTAL = By("css", "#stat_total")  # 合計チケット数
    UNTREATED = By("css", "#stat_untreated")  # 未対応件数
    IN_PROGRESS = By("css", "#stat_inprogress")  # 対応中件数
    DONE = By("css", "#stat_done")  # 完了件数
    BAR_UNTREATED = By("css", "#bar_untreated")  # 未対応グラフ
    BAR_IN_PROGRESS = By("css", "#bar_inprogress")  # 対応中グラフ
    BAR_DONE = By("css", "#bar_done")  # 完了グラフ


class SettingsLocators:
    PANEL = By("css", "#panel_settings")  # 設定画面
    HEADING = By("role", "heading", name="設定", exact=True)  # 設定の見出し
    TOGGLE = By("css", "label[for='notif_toggle']")  # 表示ラベル。inputは0pxでrole/labelは入力本体を指す
    SIGNATURE = By("placeholder", "返信メールに付与する署名を入力")  # 署名。ラベル名にカウンターが混ざる
    COUNTER = By("css", "#signature_counter")  # 文字数カウンター。roleがないためid
    SAVE = By("role", "button", name="保存する", exact=True)  # 設定パネル内に限定。詳細と同名


class PreviewFrameLocators:
    FRAME = By("css", "#preview_iframe")  # 埋め込みプレビューiframe
    STATUS = By("role", "combobox")  # iframe内のステータス
    APPLY = By("role", "button", name="適用", exact=True)  # iframe内の適用
    RESULT = By("css", "#frame_result")  # iframe内の結果


class ToastLocators:
    CONTAINER = By("css", "#toast_container")  # トーストの表示領域
    ITEM = By("css", "#toast_container .toast")  # 表示中のトースト
    CLOSE = By("role", "button", name="閉じる", exact=True)  # トーストを閉じる
