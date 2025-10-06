import pytest
from playwright.sync_api import Page, expect

def play_hand(page: Page, bidA: int, bidB: int, booksA: int, booksB: int, blindA: bool = False, blindB: bool = False):
    expect(page.locator("#bidsRow")).to_be_visible()

    # Directly set bids using JavaScript
    page.evaluate(f"state.blind10A = {str(blindA).lower()}")
    page.evaluate(f"state.blind10B = {str(blindB).lower()}")
    page.evaluate(f"$('#bidA').textContent = '{bidA}'")
    page.evaluate(f"$('#bidB').textContent = '{bidB}'")
    page.evaluate("updateUnbidNote()")
    page.evaluate("updateBlindButtons()")
    page.evaluate("togglePhaseUI()")

    # Ensure state.phase is 'books' before setting books
    if page.locator("#lockBidsBtn").is_visible() and page.evaluate("state.round > 1"):
        page.click("#lockBidsBtn")
        expect(page.locator("#status")).to_have_text("Bids locked. Now set books.")
        expect(page.locator("#booksRow")).to_be_visible()
        page.wait_for_timeout(100)

    # Set books
    # Ensure state.phase is 'books' for updateBooksSum to enable submitHandBtn
    page.evaluate("state.phase = 'books'")
    # Directly set books using JavaScript
    page.evaluate(f"$('#booksA').textContent = '{booksA}'")
    page.evaluate(f"$('#booksB').textContent = '{booksB}'")
    page.evaluate("updateBooksSum()")

    expect(page.locator("#booksA")).to_have_text(str(booksA))
    expect(page.locator("#booksB")).to_have_text(str(booksB))
    page.click("#submitHandBtn")

def test_match_end_win(page: Page):
    page.goto("file:///home/zonca/p/software/spades/index.html")

    # Enter team names and start the game
    page.fill("#teamA", "Team Alpha")
    page.fill("#teamB", "Team Beta")
    page.click("#startBtn")

    # Round 1
    expect(page.locator("#pillRound")).to_have_text("Round 1")
    page.locator("[data-for='booksA'][data-arrow='up']").click() # booksA: 7, booksB: 6
    page.click("#submitHandBtn")
    expect(page.locator("#pillA")).to_have_text("Team Alpha: 70")
    expect(page.locator("#pillB")).to_have_text("Team Beta: 60")

    # Round 2
    expect(page.locator("#pillRound")).to_have_text("Round 2")
    play_hand(page, 10, 3, 10, 3)
    expect(page.locator("#pillA")).to_have_text("Team Alpha: 170")
    expect(page.locator("#pillB")).to_have_text("Team Beta: 90")

    # Round 3
    expect(page.locator("#pillRound")).to_have_text("Round 3")
    play_hand(page, 10, 3, 10, 3)
    expect(page.locator("#pillA")).to_have_text("Team Alpha: 270")
    expect(page.locator("#pillB")).to_have_text("Team Beta: 120")

    # Round 4
    expect(page.locator("#pillRound")).to_have_text("Round 4")
    play_hand(page, 10, 3, 10, 3)
    expect(page.locator("#pillA")).to_have_text("Team Alpha: 370")
    expect(page.locator("#pillB")).to_have_text("Team Beta: 150")

    # Round 5
    expect(page.locator("#pillRound")).to_have_text("Round 5")
    play_hand(page, 10, 3, 10, 3)
    expect(page.locator("#pillA")).to_have_text("Team Alpha: 470")
    expect(page.locator("#pillB")).to_have_text("Team Beta: 180")

    # Round 6 (Winning Round)
    expect(page.locator("#pillRound")).to_have_text("Round 6")
    play_hand(page, 10, 3, 10, 3)

    # Verify winner section is displayed
    expect(page.locator("#winner")).to_be_visible()
    expect(page.locator("#winnerText")).to_have_text("Team Alpha wins!")
