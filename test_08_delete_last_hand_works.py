from playwright.sync_api import expect


def test_delete_last_hand_works(start_game):
    page = start_game("Team Alpha", "Team Beta")

    # Round 1
    expect(page.locator("#pillRound")).to_have_text("Round 1")
    page.locator("[data-for='booksA'][data-arrow='up']").click() # booksA: 7, booksB: 6
    page.click("#submitHandBtn")
    expect(page.locator("#pillA")).to_have_text("Team Alpha: 70")
    expect(page.locator("#pillB")).to_have_text("Team Beta: 60")

    # Round 2
    expect(page.locator("#pillRound")).to_have_text("Round 2")
    # Simulate bids
    page.evaluate("state.phase = 'bids'")
    page.evaluate("togglePhaseUI()")
    page.evaluate("$('#bidA').textContent = '6'")
    page.evaluate("$('#bidB').textContent = '7'")
    page.evaluate("updateUnbidNote()")
    page.click("#lockBidsBtn")
    page.evaluate("$('#booksA').textContent = '6'")
    page.evaluate("$('#booksB').textContent = '7'")
    page.evaluate("updateBooksSum()")
    page.click("#submitHandBtn")
    expect(page.locator("#pillA")).to_have_text("Team Alpha: 130")
    expect(page.locator("#pillB")).to_have_text("Team Beta: 130")

    # Delete last hand
    page.click("#deleteLastBtn")
    expect(page.locator("#pillA")).to_have_text("Team Alpha: 70")
    expect(page.locator("#pillB")).to_have_text("Team Beta: 60")
    expect(page.locator("#pillRound")).to_have_text("Round 2")
    expect(page.locator("#status")).to_have_text("Deleted last hand.")

    # Verify that the game state is correct after deletion
    # (e.g., bids are reset, phase is 'bids' for the current round)
    expect(page.locator("#bidsRow")).to_be_visible()
    expect(page.locator("#booksRow")).not_to_be_visible()
    expect(page.locator("#bidA")).to_have_text("6")
    expect(page.locator("#bidB")).to_have_text("6")
    expect(page.locator("#unbidNote")).to_have_text("Unbid books left: 1")