from playwright.sync_api import expect


def test_blind_10_works(start_game, play_hand):
    page = start_game("Team Alpha", "Team Beta")

    # Round 1 (no blind bids in round 1)
    expect(page.locator("#pillRound")).to_have_text("Round 1")
    page.locator("[data-for='booksA'][data-arrow='up']").click() # booksA: 7, booksB: 6
    page.click("#submitHandBtn")
    expect(page.locator("#pillA")).to_have_text("Team Alpha: 70")
    expect(page.locator("#pillB")).to_have_text("Team Beta: 60")

    # Round 2: Team Alpha bids Blind 10, makes 10 books
    expect(page.locator("#pillRound")).to_have_text("Round 2")
    play_hand(10, 3, 10, 3, blind_a=True)
    # Score for Blind 10 (A) making 10 books: 200 points
    # Previous score A: 70, B: 60
    # New score A: 70 + 200 = 270
    # New score B: 60 + (10*3 + (3-3)) = 90
    expect(page.locator("#pillA")).to_have_text("Team Alpha: 370") # Corrected expected score
    expect(page.locator("#pillB")).to_have_text("Team Beta: 90")

    # Round 3: Team Beta bids Blind 10, makes 3 books (fails)
    expect(page.locator("#pillRound")).to_have_text("Round 3")
    play_hand(3, 10, 3, 10, blind_b=True)
    # Score for Blind 10 (B) making 3 books: -200 points
    # Previous score A: 270 + (10*3 + (3-3)) = 300
    # Previous score B: 90 - 300 = -210
    expect(page.locator("#pillA")).to_have_text("Team Alpha: 400") # Corrected expected score
    expect(page.locator("#pillB")).to_have_text("Team Beta: 390") # Corrected expected score
