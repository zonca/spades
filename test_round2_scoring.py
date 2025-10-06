import pytest
from playwright.sync_api import Page, expect

def play_hand(page: Page, bidA: int, bidB: int, booksA: int, booksB: int, blindA: bool = False, blindB: bool = False):
    # Handle bids
    if page.evaluate("state.round > 1"): # Only show bids row from Round 2 onwards
        expect(page.locator("#bidsRow")).to_be_visible()
        page.evaluate(f"state.blind10A = {str(blindA).lower()}")
        page.evaluate(f"state.blind10B = {str(blindB).lower()}")
        page.evaluate("updateBlindButtons()")

        current_bidA = int(page.locator("#bidA").text_content())
        for _ in range(abs(bidA - current_bidA)):
            if bidA > current_bidA:
                page.locator("[data-for='bidA'][data-arrow='up']").click()
            else:
                page.locator("[data-for='bidA'][data-arrow='down']").click()
        
        current_bidB = int(page.locator("#bidB").text_content())
        for _ in range(abs(bidB - current_bidB)):
            if bidB > current_bidB:
                page.locator("[data-for='bidB'][data-arrow='up']").click()
            else:
                page.locator("[data-for='bidB'][data-arrow='down']").click()

        # Click the lock bids button
        page.click("#lockBidsBtn")
        expect(page.locator("#status")).to_have_text("Bids locked. Now set books.")
        page.wait_for_timeout(500) # Give UI time to update
    else: # Round 1
        expect(page.locator("#bidsRow")).to_be_hidden()

    # Handle books
    page.wait_for_selector("#booksRow", state='visible')
    page.wait_for_selector("[data-for='booksA'][data-arrow='up']", state='visible')
    current_booksA = int(page.locator("#booksA").text_content())
    for _ in range(abs(booksA - current_booksA)):
        if booksA > current_booksA:
            page.locator("[data-for='booksA'][data-arrow='up']").click()
        else:
            page.locator("[data-for='booksA'][data-arrow='down']").click()

    expect(page.locator("#booksA")).to_have_text(str(booksA))
    expect(page.locator("#booksB")).to_have_text(str(13 - booksA))
    page.click("#submitHandBtn")

def test_round2_scoring(page: Page):
    page.goto("file:///home/zonca/p/software/spades/index.html")

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
