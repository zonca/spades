import pytest
from playwright.sync_api import Page, expect

def test_start_game_with_team_names(page: Page):
    page.goto("file:///home/zonca/p/software/spades/spades_mobile_scorekeeper_single_page_app.html")

    # Fill in team names
    page.fill("#teamA", "Team Playwright")
    page.fill("#teamB", "Team Python")

    # Click the Start Game button
    page.click("#startBtn")

    # Assert that "Round 1" is visible on the next page
    expect(page.locator("#pillRound")).to_have_text("Round 1")
