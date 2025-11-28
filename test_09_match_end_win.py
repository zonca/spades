from playwright.sync_api import expect


def test_match_end_win(start_game, play_hand):
    page = start_game()

    # Round 1
    expect(page.locator("#pillRound")).to_have_text("Round 1")
    page.locator("[data-for='booksA'][data-arrow='up']").click() # booksA: 7, booksB: 6
    page.click("#submitHandBtn")
    expect(page.locator("#pillA")).to_have_text("Alice & Alex: 70")
    expect(page.locator("#pillB")).to_have_text("Bob & Beth: 60")

    # Round 2
    expect(page.locator("#pillRound")).to_have_text("Round 2")
    play_hand(10, 4, 10, 3)
    expect(page.locator("#pillA")).to_have_text("Alice & Alex: 170")
    expect(page.locator("#pillB")).to_have_text("Bob & Beth: 20")

    # Round 3
    expect(page.locator("#pillRound")).to_have_text("Round 3")
    play_hand(10, 4, 10, 3)
    expect(page.locator("#pillA")).to_have_text("Alice & Alex: 270")
    expect(page.locator("#pillB")).to_have_text("Bob & Beth: -20")

    # Round 4
    expect(page.locator("#pillRound")).to_have_text("Round 4")
    play_hand(10, 4, 10, 3)
    expect(page.locator("#pillA")).to_have_text("Alice & Alex: 370")
    expect(page.locator("#pillB")).to_have_text("Bob & Beth: -60")

    # Round 5
    expect(page.locator("#pillRound")).to_have_text("Round 5")
    play_hand(10, 4, 10, 3)
    expect(page.locator("#pillA")).to_have_text("Alice & Alex: 470")
    expect(page.locator("#pillB")).to_have_text("Bob & Beth: -100")

    # Round 6 (Winning Round)
    expect(page.locator("#pillRound")).to_have_text("Round 6")
    play_hand(10, 4, 10, 3)

    # Verify winner section is displayed
    expect(page.locator("#winner")).to_be_visible()
    expect(page.locator("#winnerText")).to_have_text("Alice & Alex wins!")
    expect(page.locator("#newGameBtn")).to_be_visible()
