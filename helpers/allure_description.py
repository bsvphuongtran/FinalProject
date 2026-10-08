"""Allure description helper shared by every test module."""

from __future__ import annotations

import textwrap
from collections.abc import Callable

import allure


def description_md(text: str) -> Callable[[Callable], Callable]:
    """Attach a dedented Markdown description to a test or class."""
    return allure.description(textwrap.dedent(text).strip())
