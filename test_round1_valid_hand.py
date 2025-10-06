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

def test_round1_valid_hand(page: Page):
    page.goto("file:///home/zonca/p/software/spades/index.html")

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
