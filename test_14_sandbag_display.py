from playwright.sync_api import expect


def test_sandbag_display_in_scoreboard(start_game, play_hand):
    """Test that sandbags are displayed separately in scoreboard."""
    page = start_game("Team Alpha", "Team Beta")

    # Round 1 (no bids, books only)
    expect(page.locator("#pillRound")).to_have_text("Round 1")
    page.locator("[data-for='booksA'][data-arrow='up']").click()  # booksA: 7, booksB: 6
    page.click("#submitHandBtn")
    expect(page.locator("#scorePointsA")).to_have_text("70")
    expect(page.locator("#scorePointsB")).to_have_text("60")
    # No sandbags in Round 1
    expect(page.locator("#scoreBagsA")).to_have_text("")
    expect(page.locator("#scoreBagsB")).to_have_text("")

    # Round 2: Team A bids 6, makes 10 books (4 bags). Team B bids 6, makes 3 books (no bags).
    expect(page.locator("#pillRound")).to_have_text("Round 2")
    play_hand(6, 6, 10, 3)
    expect(page.locator("#scorePointsA")).to_have_text("130")  # 70 + 10*6 = 130
    expect(page.locator("#scorePointsB")).to_have_text("0")    # 60 + (-10*6) = 0
    # Team A should have 4 sandbags displayed
    expect(page.locator("#scoreBagsA")).to_have_text("(4)")
    expect(page.locator("#scoreBagsB")).to_have_text("")


def test_sandbag_display_in_hands_table(start_game, play_hand):
    """Test that sandbags are displayed separately in hands table."""
    page = start_game("Team Alpha", "Team Beta")

    # Round 1
    page.locator("[data-for='booksA'][data-arrow='up']").click()  # booksA: 7, booksB: 6
    page.click("#submitHandBtn")
    
    # Check round 1 shows no bags
    expect(page.locator("#handsTable tbody tr:nth-child(1) td:nth-child(6)")).to_have_text("70")
    expect(page.locator("#handsTable tbody tr:nth-child(1) td:nth-child(7)")).to_have_text("60")

    # Round 2: Team A bids 6, makes 10 books (4 bags). Team B bids 6, makes 3 books (0 bags).
    play_hand(6, 6, 10, 3)
    
    # Check that round 2 shows bags for Team A
    expect(page.locator("#handsTable tbody tr:nth-child(2) td:nth-child(6)")).to_have_text("130 (4)")
    expect(page.locator("#handsTable tbody tr:nth-child(2) td:nth-child(7)")).to_have_text("0")

    # Round 3: Team A bids 6, makes 9 books (3 more bags = 7 total). Team B bids 6, makes 4 books (0 bags).
    play_hand(6, 6, 9, 4)
    
    # Check that round 3 shows cumulative bags for Team A
    expect(page.locator("#handsTable tbody tr:nth-child(3) td:nth-child(6)")).to_have_text("190 (7)")
    expect(page.locator("#handsTable tbody tr:nth-child(3) td:nth-child(7)")).to_have_text("-60")


def test_sandbag_reset_on_penalty(start_game, play_hand):
    """Test that sandbags reset to 0 after penalty is applied."""
    page = start_game("Team Alpha", "Team Beta")

    # Round 1
    page.locator("[data-for='booksA'][data-arrow='up']").click()  # booksA: 7, booksB: 6
    page.click("#submitHandBtn")
    
    # Round 2: Team A bids 6, makes 10 books (4 bags).
    play_hand(6, 6, 10, 3)
    expect(page.locator("#scoreBagsA")).to_have_text("(4)")
    
    # Round 3: Team A bids 6, makes 10 books (4 more bags = 8 total).
    play_hand(6, 6, 10, 3)
    expect(page.locator("#scoreBagsA")).to_have_text("(8)")
    
    # Round 4: Team A bids 6, makes 8 books (2 more bags = 10 total, triggers penalty).
    play_hand(6, 6, 8, 5)
    
    # After penalty, bags should reset to 0
    expect(page.locator("#scoreBagsA")).to_have_text("")
    # Score should reflect penalty: 190 + 60 - 100 = 150
    expect(page.locator("#scorePointsA")).to_have_text("150")
    
    # Verify in table that the round shows 0 bags after reset
    expect(page.locator("#handsTable tbody tr:nth-child(4) td:nth-child(6)")).to_have_text("150")


def test_sandbag_accumulation_multiple_rounds(start_game, play_hand):
    """Test sandbag accumulation across multiple rounds."""
    page = start_game("Team Alpha", "Team Beta")

    # Round 1
    page.locator("[data-for='booksA'][data-arrow='up']").click()
    page.click("#submitHandBtn")
    
    # Round 2: A gets 2 bags, B gets 0 bags (both bid 6)
    play_hand(6, 6, 8, 5)
    expect(page.locator("#scoreBagsA")).to_have_text("(2)")
    expect(page.locator("#scoreBagsB")).to_have_text("")
    expect(page.locator("#handsTable tbody tr:nth-child(2) td:nth-child(6)")).to_have_text("130 (2)")
    expect(page.locator("#handsTable tbody tr:nth-child(2) td:nth-child(7)")).to_have_text("0")
    
    # Round 3: A gets 3 more bags (5 total), B gets 0 bags
    play_hand(6, 6, 9, 4)
    expect(page.locator("#scoreBagsA")).to_have_text("(5)")
    expect(page.locator("#scoreBagsB")).to_have_text("")
    expect(page.locator("#handsTable tbody tr:nth-child(3) td:nth-child(6)")).to_have_text("190 (5)")
    expect(page.locator("#handsTable tbody tr:nth-child(3) td:nth-child(7)")).to_have_text("-60")
    
    # Round 4: A gets 1 more bag (6 total), B makes bid exactly
    play_hand(6, 6, 7, 6)
    expect(page.locator("#scoreBagsA")).to_have_text("(6)")
    expect(page.locator("#scoreBagsB")).to_have_text("")
    expect(page.locator("#handsTable tbody tr:nth-child(4) td:nth-child(6)")).to_have_text("250 (6)")
    # Team B score: -60 + 60 = 0
    expect(page.locator("#handsTable tbody tr:nth-child(4) td:nth-child(7)")).to_have_text("0")


def test_both_teams_hit_penalty_same_round(start_game, play_hand):
    """Test when both teams hit 10 sandbags in the same round."""
    page = start_game("Team Alpha", "Team Beta")

    # Round 1
    page.locator("[data-for='booksA'][data-arrow='up']").click()
    page.click("#submitHandBtn")
    
    # Round 2-4: Build up 9 bags for both teams
    # Each team bids 6, A makes 9 (3 bags), B makes 4 (0 bags)
    play_hand(6, 6, 9, 4)  # A: 3 bags, B: 0 bags
    play_hand(6, 6, 9, 4)  # A: 6 bags, B: 0 bags
    play_hand(6, 6, 9, 4)  # A: 9 bags, B: 0 bags
    
    expect(page.locator("#scoreBagsA")).to_have_text("(9)")
    expect(page.locator("#scoreBagsB")).to_have_text("")
    
    # Round 5: A gets 2 more bags (11 total), hits penalty and resets to 1
    play_hand(6, 6, 8, 5)
    
    # A should reset to 1 (11 - 10 = 1)
    expect(page.locator("#scoreBagsA")).to_have_text("(1)")
    expect(page.locator("#scoreBagsB")).to_have_text("")
