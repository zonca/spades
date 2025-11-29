from playwright.sync_api import expect


def test_round1_valid_hand(start_game):
    page = start_game()

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
    # Alice & Alex (7 books): 70 points
    # Bob & Beth (6 books): 60 points
    # New compact layout: 2 rows per round
    # Row 1 (Team A): cols #, Dealer, Team, Books(bid), Score, Total
    # Row 2 (Team B): cols Team, Books(bid), Score, Total (due to rowspan)
    expect(page.locator("#handsTable tbody tr:nth-child(1) td:nth-child(5)")).to_have_text("70")
    expect(page.locator("#handsTable tbody tr:nth-child(2) td:nth-child(3)")).to_have_text("60")
    expect(page.locator("#handsTable tbody tr:nth-child(1) td:nth-child(6)")).to_have_text("70")
    expect(page.locator("#handsTable tbody tr:nth-child(2) td:nth-child(4)")).to_have_text("60")

    # Verify total scores in pills
    expect(page.locator("#pillA")).to_have_text("Alice & Alex: 70")
    expect(page.locator("#pillB")).to_have_text("Bob & Beth: 60")
