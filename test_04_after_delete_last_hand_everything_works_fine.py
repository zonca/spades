from playwright.sync_api import expect


def test_after_delete_last_hand_everything_works_fine(start_game, play_hand):
    page = start_game("Team Alpha", "Team Beta")

    # Round 1
    expect(page.locator("#pillRound")).to_have_text("Round 1")
    page.locator("[data-for='booksA'][data-arrow='up']").click() # booksA: 7, booksB: 6
    page.click("#submitHandBtn")
    expect(page.locator("#pillA")).to_have_text("Team Alpha: 70")
    expect(page.locator("#pillB")).to_have_text("Team Beta: 60")

    # Round 2
    expect(page.locator("#pillRound")).to_have_text("Round 2")
    play_hand(6, 7, 6, 7)
    expect(page.locator("#pillA")).to_have_text("Team Alpha: 130")
    expect(page.locator("#pillB")).to_have_text("Team Beta: 130")

    # Delete last hand
    page.click("#deleteLastBtn")
    expect(page.locator("#pillA")).to_have_text("Team Alpha: 70")
    expect(page.locator("#pillB")).to_have_text("Team Beta: 60")
    expect(page.locator("#pillRound")).to_have_text("Round 2")
    expect(page.locator("#status")).to_have_text("Deleted last hand.")

    # Play another hand in Round 2
    play_hand(6, 7, 6, 7)
    expect(page.locator("#pillA")).to_have_text("Team Alpha: 130")
    expect(page.locator("#pillB")).to_have_text("Team Beta: 130")