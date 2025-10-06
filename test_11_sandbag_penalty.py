from playwright.sync_api import expect


def test_sandbag_penalty(start_game, play_hand):
    page = start_game("Team Alpha", "Team Beta")

    # Round 1 (no bids, books only)
    expect(page.locator("#pillRound")).to_have_text("Round 1")
    page.locator("[data-for='booksA'][data-arrow='up']").click()  # booksA: 7, booksB: 6
    page.click("#submitHandBtn")
    expect(page.locator("#pillA")).to_have_text("Team Alpha: 70")
    expect(page.locator("#pillB")).to_have_text("Team Beta: 60")

    # Round 2: Team A bids 6, makes 10 books (4 bags). Team B bids 6, makes 3 books (-30 points).
    expect(page.locator("#pillRound")).to_have_text("Round 2")
    play_hand(6, 6, 10, 3)
    expect(page.locator("#pillA")).to_have_text("Team Alpha: 134")  # 70 + (10*6 + 4) = 70 + 64 = 134
    expect(page.locator("#pillB")).to_have_text("Team Beta: 0")    # 60 + (-10*6) = 60 - 60 = 0

    # Round 3: Team A bids 6, makes 10 books (4 bags). Team B bids 6, makes 3 books (-30 points).
    expect(page.locator("#pillRound")).to_have_text("Round 3")
    play_hand(6, 6, 10, 3)
    expect(page.locator("#pillA")).to_have_text("Team Alpha: 198")  # 134 + (10*6 + 4) = 134 + 64 = 198
    expect(page.locator("#pillB")).to_have_text("Team Beta: -60")   # 0 + (-10*6) = 0 - 60 = -60

    # Round 4: Team A bids 6, makes 8 books (2 bags). Total bags A: 8 + 2 = 10. Penalty applies.
    # Team B bids 6, makes 5 books (-10 points).
    expect(page.locator("#pillRound")).to_have_text("Round 4")
    play_hand(6, 6, 8, 5)
    # Score A for hand: (10*6 + 2) = 62. Bags A: 8 + 2 = 10. Penalty: -100. New bags A: 0.
    # Total A: 198 + 62 - 100 = 160
    # Score B for hand: (-10*6) = -60. Bags B: 0 + 0 = 0. No penalty.
    # Total B: -60 - 60 = -120
    expect(page.locator("#pillA")).to_have_text("Team Alpha: 160")
    expect(page.locator("#pillB")).to_have_text("Team Beta: -120")
