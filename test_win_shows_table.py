import pytest
from playwright.sync_api import Page, expect

def play_hand(page: Page, bidA: int, bidB: int, booksA: int, booksB: int, blindA: bool = False, blindB: bool = False):
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

    page.evaluate("state.phase = 'books'")
    page.evaluate("state.lockedBids = true")
    page.evaluate("togglePhaseUI()")
    page.evaluate("$('#status').textContent='Bids locked. Now set books.'")
    page.wait_for_timeout(500)

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

def test_win_shows_table(page: Page):
    page.goto("file:///home/zonca/p/software/spades/index.html")

    # Enter team names and start the game
    page.fill("#teamA", "Team Alpha")
    page.fill("#teamB", "Team Beta")
    page.click("#startBtn")

    # Round 1: Team Alpha gets 70, Team Beta gets 60
    expect(page.locator("#pillRound")).to_have_text("Round 1")
    page.locator("[data-for='booksA'][data-arrow='up']").click() # booksA: 7, booksB: 6
    page.click("#submitHandBtn")
    expect(page.locator("#pillA")).to_have_text("Team Alpha: 70")
    expect(page.locator("#pillB")).to_have_text("Team Beta: 60")

    # Round 2: Team Alpha gets 100, Team Beta gets 30 (total A: 170, B: 90)
    expect(page.locator("#pillRound")).to_have_text("Round 2")
    play_hand(page, 10, 3, 10, 3)
    expect(page.locator("#pillA")).to_have_text("Team Alpha: 170")
    expect(page.locator("#pillB")).to_have_text("Team Beta: 90")

    # Round 3: Team Alpha gets 100, Team Beta gets 30 (total A: 270, B: 120)
    expect(page.locator("#pillRound")).to_have_text("Round 3")
    play_hand(page, 10, 3, 10, 3)
    expect(page.locator("#pillA")).to_have_text("Team Alpha: 270")
    expect(page.locator("#pillB")).to_have_text("Team Beta: 120")

    # Round 4: Team Alpha gets 100, Team Beta gets 30 (total A: 370, B: 150)
    expect(page.locator("#pillRound")).to_have_text("Round 4")
    play_hand(page, 10, 3, 10, 3)
    expect(page.locator("#pillA")).to_have_text("Team Alpha: 370")
    expect(page.locator("#pillB")).to_have_text("Team Beta: 150")

    # Round 5: Team Alpha gets 100, Team Beta gets 30 (total A: 470, B: 180)
    expect(page.locator("#pillRound")).to_have_text("Round 5")
    play_hand(page, 10, 3, 10, 3)
    expect(page.locator("#pillA")).to_have_text("Team Alpha: 470")
    expect(page.locator("#pillB")).to_have_text("Team Beta: 180")

    # Round 6: Team Alpha gets 100, Team Beta gets 30 (total A: 570, B: 210) - Team Alpha wins
    expect(page.locator("#pillRound")).to_have_text("Round 6")
    play_hand(page, 10, 3, 10, 3)
    expect(page.locator("#pillA")).to_have_text("Team Alpha: 570")
    expect(page.locator("#pillB")).to_have_text("Team Beta: 210")

    # Assert that the hands table is visible
    expect(page.locator("#handsTable")).to_be_visible()

    # Assert that the winner message is displayed within the game section
    expect(page.locator("#status")).to_have_text("Team Alpha wins!")

    # Assert that input controls are hidden
    expect(page.locator("#bidsRow")).not_to_be_visible()
    expect(page.locator("#booksRow")).not_to_be_visible()
    expect(page.locator(".toolbar:has(#deleteLastBtn)")).not_to_be_visible()
    expect(page.locator("#submitHandBtn")).not_to_be_visible()
