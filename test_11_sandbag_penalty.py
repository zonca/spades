from playwright.sync_api import expect


def test_sandbag_penalty(start_game, play_hand):
    page = start_game()

    # Round 1 (no bids, books only)
    expect(page.locator("#pillRound")).to_have_text("Round 1")
    page.locator("[data-for='booksA'][data-arrow='up']").click()  # booksA: 7, booksB: 6
    page.click("#submitHandBtn")
    expect(page.locator("#pillA")).to_have_text("Alice & Alex: 70")
    expect(page.locator("#pillB")).to_have_text("Bob & Beth: 60")

    # Round 2: Team A bids 6, makes 10 books (4 bags). Team B bids 6, makes 3 books (-60 points).
    expect(page.locator("#pillRound")).to_have_text("Round 2")
    play_hand(6, 6, 10, 3)
    expect(page.locator("#pillA")).to_have_text("Alice & Alex: 130 (4)")  # 70 + 10*6 = 130, 4 bags
    expect(page.locator("#pillB")).to_have_text("Bob & Beth: 0")    # 60 + (-10*6) = 0, 0 bags

    # Round 3: Team A bids 6, makes 10 books (4 bags). Team B bids 6, makes 3 books (-60 points).
    expect(page.locator("#pillRound")).to_have_text("Round 3")
    play_hand(6, 6, 10, 3)
    expect(page.locator("#pillA")).to_have_text("Alice & Alex: 190 (8)")  # 130 + 10*6 = 190, 8 bags
    expect(page.locator("#pillB")).to_have_text("Bob & Beth: -60")   # 0 + (-10*6) = -60, 0 bags

    # Round 4: Team A bids 6, makes 8 books (2 bags). Total bags A: 8 + 2 = 10. Penalty applies.
    # Team B bids 6, makes 5 books (-60 points).
    expect(page.locator("#pillRound")).to_have_text("Round 4")
    play_hand(6, 6, 8, 5)
    # Score A for hand: 10*6 = 60. Bags A: 8 + 2 = 10. Penalty: -100. New bags A: 0.
    # Total A: 190 + 60 - 100 = 150, bags reset to 0
    # Score B for hand: (-10*6) = -60. Bags B: 0 + 0 = 0. No penalty.
    # Total B: -60 - 60 = -120
    expect(page.locator("#pillA")).to_have_text("Alice & Alex: 150")  # Bags reset to 0 after penalty
    expect(page.locator("#pillB")).to_have_text("Bob & Beth: -120")
