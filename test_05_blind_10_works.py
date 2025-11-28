from playwright.sync_api import expect


def test_blind_10_works(start_game, play_hand):
    page = start_game()

    # Round 1 (no blind bids in round 1)
    expect(page.locator("#pillRound")).to_have_text("Round 1")
    page.locator("[data-for='booksA'][data-arrow='up']").click() # booksA: 7, booksB: 6
    page.click("#submitHandBtn")
    expect(page.locator("#pillA")).to_have_text("Alice & Alex: 70")
    expect(page.locator("#pillB")).to_have_text("Bob & Beth: 60")

    # Round 2: Alice & Alex bids Blind 10, makes 10 books
    expect(page.locator("#pillRound")).to_have_text("Round 2")
    play_hand(10, 4, 10, 3, blind_a=True)
    # Score for Blind 10 (A) making 10 books: 200 points
    # Previous score A: 70, B: 60
    # New score A: 70 + 200 = 270
    # New score B: 60 - 40 = 20
    expect(page.locator("#pillA")).to_have_text("Alice & Alex: 270")
    expect(page.locator("#pillB")).to_have_text("Bob & Beth: 20")

    # Round 3: Bob & Beth bids Blind 10, makes 10 books
    expect(page.locator("#pillRound")).to_have_text("Round 3")
    play_hand(4, 10, 3, 10, blind_b=True)
    # Score for Blind 10 (B) making 10 books: 200 points
    # Previous score A: 270 - 40 = 230
    # Previous score B: 20 + 200 = 220
    expect(page.locator("#pillA")).to_have_text("Alice & Alex: 230")
    expect(page.locator("#pillB")).to_have_text("Bob & Beth: 220")
