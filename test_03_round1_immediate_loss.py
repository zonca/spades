from playwright.sync_api import expect


def test_round1_immediate_loss(start_game):
    page = start_game("Team Alpha", "Team Beta")

    # Verify Bids section is hidden in Round 1
    expect(page.locator("#bidsRow")).to_be_hidden()
    expect(page.locator("#pillRound")).to_have_text("Round 1")

    # Set books for Team A to 3 (less than 4) and Team B to 10
    # Initial booksA is 6, booksB is 7
    # Click booksA down 3 times (6 -> 5 -> 4 -> 3)
    page.locator("[data-for='booksA'][data-arrow='down']").click()
    page.locator("[data-for='booksA'][data-arrow='down']").click()
    page.locator("[data-for='booksA'][data-arrow='down']").click()
    expect(page.locator("#booksA")).to_have_text("3")
    expect(page.locator("#booksB")).to_have_text("10") # Should auto-adjust

    # Submit the hand
    page.click("#submitHandBtn")

    # Verify winner section is displayed
    expect(page.locator("#winner")).not_to_be_visible()
    expect(page.locator("#status")).to_have_text("Team Beta wins!")
