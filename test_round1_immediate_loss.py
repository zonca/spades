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

def test_round1_immediate_loss(page: Page):
    page.goto("file:///home/zonca/p/software/spades/index.html")

    # Enter team names and start the game
    page.fill("#teamA", "Team Alpha")
    page.fill("#teamB", "Team Beta")
    page.click("#startBtn")

    # Verify Bids section is hidden in Round 1
    expect(page.locator("#bidsRow")).to_be_hidden()
    expect(page.locator("#pillRound")).to_have_text("Round 1")

    # Set books for Team A to 3 (less than 4) and Team B to 10
    # Initial booksA is 6, booksB is 7
    # Click booksA down 3 times (6 -> 5 -> 4 -> 3)
    page.locator("[data-for='booksA'][data-arrow='down']").click()
    page.locator("[data-for='booksA'][data-arrow='down']").click()
    page.locator("[data-for='booksA'][data-arrow='down']").click()
    expect(page.locator("#booksA")).to_have_text("3")
    expect(page.locator("#booksB")).to_have_text("10") # Should auto-adjust

    # Submit the hand
    page.click("#submitHandBtn")

    # Verify winner section is displayed
    expect(page.locator("#winner")).not_to_be_visible()
    expect(page.locator("#status")).to_have_text("<strong>Team Beta</strong> wins!")
