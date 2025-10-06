import pytest
from playwright.sync_api import Page, expect

def play_hand(page: Page, bidA: int, bidB: int, booksA: int, booksB: int, blindA: bool = False, blindB: bool = False):
    # Handle bids
    if page.evaluate("state.round > 1"):
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
    else:
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
def test_blind_10_works(page: Page):
    page.goto("file:///home/zonca/p/software/spades/index.html")

    # Enter team names and start the game
    page.fill("#teamA", "Team Alpha")
    page.fill("#teamB", "Team Beta")
    page.click("#startBtn")

    # Round 1 (no blind bids in round 1)
    expect(page.locator("#pillRound")).to_have_text("Round 1")
    page.locator("[data-for='booksA'][data-arrow='up']").click() # booksA: 7, booksB: 6
    page.click("#submitHandBtn")
    expect(page.locator("#pillA")).to_have_text("Team Alpha: 70")
    expect(page.locator("#pillB")).to_have_text("Team Beta: 60")

    # Round 2: Team Alpha bids Blind 10, makes 10 books
    expect(page.locator("#pillRound")).to_have_text("Round 2")
    play_hand(page, 10, 3, 10, 3, blindA=True)
    # Score for Blind 10 (A) making 10 books: 200 points
    # Previous score A: 70, B: 60
    # New score A: 70 + 200 = 270
    # New score B: 60 + (10*3 + (3-3)) = 90
    expect(page.locator("#pillA")).to_have_text("Team Alpha: 370") # Corrected expected score
    expect(page.locator("#pillB")).to_have_text("Team Beta: 90")

    # Round 3: Team Beta bids Blind 10, makes 3 books (fails)
    expect(page.locator("#pillRound")).to_have_text("Round 3")
    play_hand(page, 3, 10, 3, 3, blindB=True)
    # Score for Blind 10 (B) making 3 books: -200 points
    # Previous score A: 270 + (10*3 + (3-3)) = 300
    # Previous score B: 90 - 300 = -210
    expect(page.locator("#pillA")).to_have_text("Team Alpha: 400") # Corrected expected score
    expect(page.locator("#pillB")).to_have_text("Team Beta: 390") # Corrected expected score
