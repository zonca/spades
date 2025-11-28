from playwright.sync_api import expect


def test_win_shows_table(start_game, play_hand):
    page = start_game()

    # Round 1: Alice & Alex gets 70, Bob & Beth gets 60
    expect(page.locator("#pillRound")).to_have_text("Round 1")
    page.locator("[data-for='booksA'][data-arrow='up']").click() # booksA: 7, booksB: 6
    page.click("#submitHandBtn")
    expect(page.locator("#pillA")).to_have_text("Alice & Alex: 70")
    expect(page.locator("#pillB")).to_have_text("Bob & Beth: 60")

    # Round 2: Alice & Alex gets 100, Bob & Beth loses 40 (total A: 170, B: 20)
    expect(page.locator("#pillRound")).to_have_text("Round 2")
    play_hand(10, 4, 10, 3)
    expect(page.locator("#pillA")).to_have_text("Alice & Alex: 170")
    expect(page.locator("#pillB")).to_have_text("Bob & Beth: 20")

    # Round 3: Alice & Alex gets 100, Bob & Beth loses 40 (total A: 270, B: -20)
    expect(page.locator("#pillRound")).to_have_text("Round 3")
    play_hand(10, 4, 10, 3)
    expect(page.locator("#pillA")).to_have_text("Alice & Alex: 270")
    expect(page.locator("#pillB")).to_have_text("Bob & Beth: -20")

    # Round 4: Alice & Alex gets 100, Bob & Beth loses 40 (total A: 370, B: -60)
    expect(page.locator("#pillRound")).to_have_text("Round 4")
    play_hand(10, 4, 10, 3)
    expect(page.locator("#pillA")).to_have_text("Alice & Alex: 370")
    expect(page.locator("#pillB")).to_have_text("Bob & Beth: -60")

    # Round 5: Alice & Alex gets 100, Bob & Beth loses 40 (total A: 470, B: -100)
    expect(page.locator("#pillRound")).to_have_text("Round 5")
    play_hand(10, 4, 10, 3)
    expect(page.locator("#pillA")).to_have_text("Alice & Alex: 470")
    expect(page.locator("#pillB")).to_have_text("Bob & Beth: -100")

    # Round 6: Alice & Alex gets 100, Bob & Beth loses 40 (total A: 570, B: -140) - Alice & Alex wins
    expect(page.locator("#pillRound")).to_have_text("Round 6")
    play_hand(10, 4, 10, 3)
    expect(page.locator("#pillA")).to_have_text("Alice & Alex: 570")
    expect(page.locator("#pillB")).to_have_text("Bob & Beth: -140")

    # Assert that the hands table is visible
    expect(page.locator("#handsTable")).to_be_visible()

    # Assert that the winner message is displayed within the game section
    expect(page.locator("#winnerText")).to_have_text("Alice & Alex wins!")
    expect(page.locator("#status")).to_have_text("")
    expect(page.locator("#winner .winner-actions")).to_be_visible()

    # Assert that input controls are hidden
    expect(page.locator("#bidsRow")).not_to_be_visible()
    expect(page.locator("#booksRow")).not_to_be_visible()
    expect(page.locator(".toolbar:has(#deleteLastBtn)")).not_to_be_visible()
    expect(page.locator("#submitHandBtn")).not_to_be_visible()
