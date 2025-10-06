from playwright.sync_api import expect


def test_match_end_win(start_game, play_hand):
    page = start_game("Team Alpha", "Team Beta")

    # Round 1
    expect(page.locator("#pillRound")).to_have_text("Round 1")
    page.locator("[data-for='booksA'][data-arrow='up']").click() # booksA: 7, booksB: 6
    page.click("#submitHandBtn")
    expect(page.locator("#pillA")).to_have_text("Team Alpha: 70")
    expect(page.locator("#pillB")).to_have_text("Team Beta: 60")

    # Round 2
    expect(page.locator("#pillRound")).to_have_text("Round 2")
    play_hand(10, 3, 10, 3)
    expect(page.locator("#pillA")).to_have_text("Team Alpha: 170")
    expect(page.locator("#pillB")).to_have_text("Team Beta: 90")

    # Round 3
    expect(page.locator("#pillRound")).to_have_text("Round 3")
    play_hand(10, 3, 10, 3)
    expect(page.locator("#pillA")).to_have_text("Team Alpha: 270")
    expect(page.locator("#pillB")).to_have_text("Team Beta: 120")

    # Round 4
    expect(page.locator("#pillRound")).to_have_text("Round 4")
    play_hand(10, 3, 10, 3)
    expect(page.locator("#pillA")).to_have_text("Team Alpha: 370")
    expect(page.locator("#pillB")).to_have_text("Team Beta: 150")

    # Round 5
    expect(page.locator("#pillRound")).to_have_text("Round 5")
    play_hand(10, 3, 10, 3)
    expect(page.locator("#pillA")).to_have_text("Team Alpha: 470")
    expect(page.locator("#pillB")).to_have_text("Team Beta: 180")

    # Round 6 (Winning Round)
    expect(page.locator("#pillRound")).to_have_text("Round 6")
    play_hand(10, 3, 10, 3)

    # Verify winner section is displayed
    expect(page.locator("#winner")).not_to_be_visible()
    expect(page.locator("#status")).to_have_text("Team Alpha wins!")
