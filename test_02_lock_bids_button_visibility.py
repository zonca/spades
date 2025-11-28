from playwright.sync_api import expect


def test_lock_bids_button_visibility_in_round3(start_game, play_hand):
    page = start_game()
    expect(page.locator("#pillRound")).to_have_text("Round 1")


    page.locator("[data-for='booksA'][data-arrow='up']").click() # booksA: 7, booksB: 6
    page.click("#submitHandBtn")
    expect(page.locator("#pillA")).to_have_text("Alice & Alex: 70")
    expect(page.locator("#pillB")).to_have_text("Bob & Beth: 60")

    # Round 2
    expect(page.locator("#pillRound")).to_have_text("Round 2")
    play_hand(6, 7, 6, 7) # Play a normal hand
    expect(page.locator("#pillA")).to_have_text("Alice & Alex: 130")
    expect(page.locator("#pillB")).to_have_text("Bob & Beth: 130")

    # Round 3: Check for lock bids button
    expect(page.locator("#pillRound")).to_have_text("Round 3")
    expect(page.locator("#lockBidsBtn")).to_be_visible() # This should fail initially
