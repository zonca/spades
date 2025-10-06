from __future__ import annotations

from pathlib import Path
from typing import Callable

import pytest
from playwright.sync_api import Page, expect


@pytest.fixture(scope="session")
def app_url() -> str:
    """Return the absolute file:// URL for the local index.html."""
    return Path(__file__).resolve().with_name("index.html").as_uri()


@pytest.fixture
def start_game(page: Page, app_url: str) -> Callable[[str, str], Page]:
    """Load the app, fill in team names, and click Start."""

    def _start(team_a: str = "Team Alpha", team_b: str = "Team Beta") -> Page:
        page.goto(app_url)
        page.on("console", lambda msg: print(f"Browser console: {msg.text}"))
        page.fill("#teamA", team_a)
        page.fill("#teamB", team_b)
        page.click("#startBtn")
        return page

    return _start


@pytest.fixture
def play_hand(page: Page) -> Callable[[int, int, int, int, bool, bool], None]:
    """Advance the game by playing a hand with the given bids/books."""

    def _play_hand(
        bid_a: int,
        bid_b: int,
        books_a: int,
        books_b: int,
        blind_a: bool = False,
        blind_b: bool = False,
    ) -> None:
        if page.evaluate("state.round > 1"):
            expect(page.locator("#bidsRow")).to_be_visible()
            page.evaluate(f"state.blind10A = {str(blind_a).lower()}")
            page.evaluate(f"state.blind10B = {str(blind_b).lower()}")
            page.evaluate("updateBlindButtons()")

            bid_a_text = page.locator("#bidA").text_content()
            assert bid_a_text is not None
            current_bid_a = int(bid_a_text)
            for _ in range(abs(bid_a - current_bid_a)):
                if bid_a > current_bid_a:
                    page.locator("[data-for='bidA'][data-arrow='up']").click()
                else:
                    page.locator("[data-for='bidA'][data-arrow='down']").click()

            bid_b_text = page.locator("#bidB").text_content()
            assert bid_b_text is not None
            current_bid_b = int(bid_b_text)
            for _ in range(abs(bid_b - current_bid_b)):
                if bid_b > current_bid_b:
                    page.locator("[data-for='bidB'][data-arrow='up']").click()
                else:
                    page.locator("[data-for='bidB'][data-arrow='down']").click()

            page.click("#lockBidsBtn")
            expect(page.locator("#status")).to_have_text("Bids locked. Now set books.")
            page.wait_for_timeout(500)
        else:
            expect(page.locator("#bidsRow")).to_be_hidden()

        page.wait_for_selector("#booksRow", state="visible")
        page.wait_for_selector("[data-for='booksA'][data-arrow='up']", state="visible")
        books_a_text = page.locator("#booksA").text_content()
        assert books_a_text is not None
        current_books_a = int(books_a_text)
        for _ in range(abs(books_a - current_books_a)):
            if books_a > current_books_a:
                page.locator("[data-for='booksA'][data-arrow='up']").click()
            else:
                page.locator("[data-for='booksA'][data-arrow='down']").click()

        expect(page.locator("#booksA")).to_have_text(str(books_a))
        expect(page.locator("#booksB")).to_have_text(str(books_b))
        page.click("#submitHandBtn")

    return _play_hand
