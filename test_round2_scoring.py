import pytest
from playwright.sync_api import Page, expect

def test_round2_scoring(page: Page):
    page.goto("file:///home/zonca/p/software/spades/spades_mobile_scorekeeper_single_page_app.html")

    # Enter team names and start the game
    page.fill("#teamA", "Team Alpha")
    page.fill("#teamB", "Team Beta")
    page.click("#startBtn")

    # Play a valid Round 1 hand to get to Round 2
    # Set booksA to 7 and booksB to 6
    page.locator("[data-for='booksA'][data-arrow='up']").click()
    expect(page.locator("#booksA")).to_have_text("7")
    expect(page.locator("#booksB")).to_have_text("6")
    page.click("#submitHandBtn")

    # Verify Round 2 is displayed
    expect(page.locator("#pillRound")).to_have_text("Round 2")
    expect(page.locator("#bidsRow")).to_be_visible()

    # Set bids for Round 2
    # Team A bid: 6 (initial value)
    # Team B bid: 7 (initial value)
    # Let's keep initial bids: bidA=6, bidB=6
    # We need to change bidB to 7
    page.locator("[data-for='bidB'][data-arrow='up']").click()
    expect(page.locator("#bidA")).to_have_text("6")
    expect(page.locator("#bidB")).to_have_text("7")

    # Lock bids
    page.click("#lockBidsBtn")
    expect(page.locator("#status")).to_have_text("Bids locked. Now set books.")

    # Set books for Round 2
    # Team A books: 7 (initial value is 6, click up once)
    # Team B books: 6 (initial value is 7, click down once)
    page.locator("[data-for='booksA'][data-arrow='up']").click()
    expect(page.locator("#booksA")).to_have_text("7")
    expect(page.locator("#booksB")).to_have_text("6")

    # Submit the hand
    page.click("#submitHandBtn")

    # Verify Round 3 is displayed
    expect(page.locator("#pillRound")).to_have_text("Round 3")

    # Verify scores in the table for Round 2
    # Round 1: Team Alpha: 70, Team Beta: 60
    # Round 2: Team A bid 6, books 7 -> Score = 10*6 + (7-6) = 61
    #          Team B bid 7, books 6 -> Score = -10*7 = -70
    expect(page.locator("#handsTable tbody tr:nth-child(2) td:nth-child(4)")).to_have_text("61")
    expect(page.locator("#handsTable tbody tr:nth-child(2) td:nth-child(5)")).to_have_text("-70")

    # Verify total scores in pills
    # Total A: 70 + 61 = 131
    # Total B: 60 - 70 = -10
    expect(page.locator("#pillA")).to_have_text("Team Alpha: 131")
    expect(page.locator("#pillB")).to_have_text("Team Beta: -10")
