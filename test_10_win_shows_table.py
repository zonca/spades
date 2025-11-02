from playwright.sync_api import expect


def test_win_shows_table(start_game, play_hand):
    page = start_game("Team Alpha", "Team Beta")

    # Round 1: Team Alpha gets 70, Team Beta gets 60
    expect(page.locator("#pillRound")).to_have_text("Round 1")
    page.locator("[data-for='booksA'][data-arrow='up']").click() # booksA: 7, booksB: 6
    page.click("#submitHandBtn")
    expect(page.locator("#pillA")).to_have_text("Team Alpha: 70")
    expect(page.locator("#pillB")).to_have_text("Team Beta: 60")

    # Round 2: Team Alpha gets 100, Team Beta loses 40 (total A: 170, B: 20)
    expect(page.locator("#pillRound")).to_have_text("Round 2")
    play_hand(10, 4, 10, 3)
    expect(page.locator("#pillA")).to_have_text("Team Alpha: 170")
    expect(page.locator("#pillB")).to_have_text("Team Beta: 20")

    # Round 3: Team Alpha gets 100, Team Beta loses 40 (total A: 270, B: -20)
    expect(page.locator("#pillRound")).to_have_text("Round 3")
    play_hand(10, 4, 10, 3)
    expect(page.locator("#pillA")).to_have_text("Team Alpha: 270")
    expect(page.locator("#pillB")).to_have_text("Team Beta: -20")

    # Round 4: Team Alpha gets 100, Team Beta loses 40 (total A: 370, B: -60)
    expect(page.locator("#pillRound")).to_have_text("Round 4")
    play_hand(10, 4, 10, 3)
    expect(page.locator("#pillA")).to_have_text("Team Alpha: 370")
    expect(page.locator("#pillB")).to_have_text("Team Beta: -60")

    # Round 5: Team Alpha gets 100, Team Beta loses 40 (total A: 470, B: -100)
    expect(page.locator("#pillRound")).to_have_text("Round 5")
    play_hand(10, 4, 10, 3)
    expect(page.locator("#pillA")).to_have_text("Team Alpha: 470")
    expect(page.locator("#pillB")).to_have_text("Team Beta: -100")

    # Round 6: Team Alpha gets 100, Team Beta loses 40 (total A: 570, B: -140) - Team Alpha wins
    expect(page.locator("#pillRound")).to_have_text("Round 6")
    play_hand(10, 4, 10, 3)
    expect(page.locator("#pillA")).to_have_text("Team Alpha: 570")
    expect(page.locator("#pillB")).to_have_text("Team Beta: -140")

    # Assert that the hands table is visible
    expect(page.locator("#handsTable")).to_be_visible()

    # Assert that the winner message is displayed within the game section
    expect(page.locator("#status")).to_have_text("Team Alpha wins!")

    # Assert that input controls are hidden
    expect(page.locator("#bidsRow")).not_to_be_visible()
    expect(page.locator("#booksRow")).not_to_be_visible()
    expect(page.locator(".toolbar:has(#deleteLastBtn)")).not_to_be_visible()
    expect(page.locator("#submitHandBtn")).not_to_be_visible()
