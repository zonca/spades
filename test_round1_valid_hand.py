import pytest
from playwright.sync_api import Page, expect

def test_round1_valid_hand(page: Page):
    page.goto("file:///home/zonca/p/software/spades/spades_mobile_scorekeeper_single_page_app.html")

    # Enter team names and start the game
    page.fill("#teamA", "Team Alpha")
    page.fill("#teamB", "Team Beta")
    page.click("#startBtn")

    # Verify Bids section is hidden in Round 1
    expect(page.locator("#bidsRow")).to_be_hidden()
    expect(page.locator("#pillRound")).to_have_text("Round 1")

    # Set books for Team A and Team B (e.g., 7 for A, 6 for B)
    # Initial values are 6 for A and 7 for B, so we'll adjust if needed
    # Let's set booksA to 7 and booksB to 6
    # Current booksA is 6, so click up once
    page.locator("[data-for='booksA'][data-arrow='up']").click()
    expect(page.locator("#booksA")).to_have_text("7")
    expect(page.locator("#booksB")).to_have_text("6") # Should auto-adjust

    # Submit the hand
    page.click("#submitHandBtn")

    # Verify Round 2 is displayed
    expect(page.locator("#pillRound")).to_have_text("Round 2")

    # Verify scores in the table
    # Round 1: Score = 10 * books
    # Team Alpha (7 books): 70 points
    # Team Beta (6 books): 60 points
    expect(page.locator("#handsTable tbody tr:nth-child(1) td:nth-child(4)")).to_have_text("70")
    expect(page.locator("#handsTable tbody tr:nth-child(1) td:nth-child(5)")).to_have_text("60")
    expect(page.locator("#handsTable tbody tr:nth-child(1) td:nth-child(6)")).to_have_text("70")
    expect(page.locator("#handsTable tbody tr:nth-child(1) td:nth-child(7)")).to_have_text("60")

    # Verify total scores in pills
    expect(page.locator("#pillA")).to_have_text("Team Alpha: 70")
    expect(page.locator("#pillB")).to_have_text("Team Beta: 60")
