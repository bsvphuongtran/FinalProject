"""Aggregate of the screen objects for one browser page."""

from __future__ import annotations

from playwright.sync_api import Page

from pages.header_page import HeaderPage
from pages.login_page import LoginPage
from pages.notification_page import NotificationPage
from pages.settings_page import SettingsPage
from pages.stats_page import StatsPage
from pages.ticket_detail_page import TicketDetailPage
from pages.ticket_drawer_page import TicketDrawerPage
from pages.ticket_list_page import TicketListPage


class SupportApp:
    """Pages that share one Playwright page. The fixture builds this object."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.login = LoginPage(page)
        self.header = HeaderPage(page)
        self.tickets = TicketListPage(page)
        self.detail = TicketDetailPage(page)
        self.drawer = TicketDrawerPage(page)
        self.notifications = NotificationPage(page)
        self.stats = StatsPage(page)
        self.settings = SettingsPage(page)
