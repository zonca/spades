from playwright.sync_api import expect


def test_round2_scoring(start_game, play_hand):
    page = start_game()

    # Play a valid Round 1 hand to get to Round 2
    # Set booksA to 7 and booksB to 6
    page.locator("[data-for='booksA'][data-arrow='up']").click()
    expect(page.locator("#booksA")).to_have_text("7")
    expect(page.locator("#booksB")).to_have_text("6")
    page.click("#submitHandBtn")

    # Play Round 2
    expect(page.locator("#pillRound")).to_have_text("Round 2")
    expect(page.locator("#bidsRow")).to_be_visible()
    play_hand(6, 7, 7, 6)

    # Verify Round 3 is displayed
    expect(page.locator("#pillRound")).to_have_text("Round 3")

    # Verify scores in the table for Round 2
    # Round 1: Alice & Alex: 70, Bob & Beth: 60
    # Round 2: Team A bid 6, books 7 -> Score = 10*6 = 60 (1 sandbag not counted in score)
    #          Team B bid 7, books 6 -> Score = -10*7 = -70
    # New compact layout: Row 3 is Team A of round 2, Row 4 is Team B of round 2
    expect(page.locator("#handsTable tbody tr:nth-child(3) td:nth-child(5)")).to_have_text("60")
    expect(page.locator("#handsTable tbody tr:nth-child(4) td:nth-child(3)")).to_have_text("-70")

    # Verify total scores in pills
    # Total A: 70 + 60 = 130 with 1 sandbag
    # Total B: 60 - 70 = -10 with 0 sandbags
    expect(page.locator("#pillA")).to_have_text("Alice & Alex: 130 (1)")
    expect(page.locator("#pillB")).to_have_text("Bob & Beth: -10")
