from playwright.sync_api import expect


def _finish_round_one(page) -> None:
    """Progress through round one so bidding UI becomes visible."""
    expect(page.locator("#pillRound")).to_have_text("Round 1")
    page.locator("[data-for='booksA'][data-arrow='up']").click()
    expect(page.locator("#booksA")).to_have_text("7")
    expect(page.locator("#booksB")).to_have_text("6")
    page.click("#submitHandBtn")
    expect(page.locator("#pillRound")).to_have_text("Round 2")
    expect(page.locator("#bidsRow")).to_be_visible()


def test_nil_sets_bid_to_zero_and_restores_previous_value(start_game):
    page = start_game("Team Alpha", "Team Beta")
    _finish_round_one(page)

    # Prepare by lowering Team A's bid to 5 so we can ensure it restores.
    page.locator("[data-for='bidA'][data-arrow='down']").click()
    expect(page.locator("#bidA")).to_have_text("5")
    expect(page.locator("#unbidNote")).to_have_text("Unbid books left: 2")

    # Enable Nil – bid should drop to 0 and arrows should disable.
    page.click("#nilA")
    expect(page.locator("#nilA")).to_have_text("Nil ✓")
    expect(page.locator("#bidA")).to_have_text("0")
    expect(page.locator("#unbidNote")).to_have_text("Unbid books left: 7")
    expect(page.locator("[data-for='bidA'][data-arrow='down']")).to_be_disabled()
    expect(page.locator("[data-for='bidA'][data-arrow='up']")).to_be_disabled()

    # Disable Nil – bid should restore to previous (min 4) and controls re-enable.
    page.click("#nilA")
    expect(page.locator("#nilA")).to_have_text("Nil")
    expect(page.locator("#bidA")).to_have_text("5")
    expect(page.locator("#unbidNote")).to_have_text("Unbid books left: 2")
    expect(page.locator("[data-for='bidA'][data-arrow='down']")).not_to_be_disabled()
    expect(page.locator("[data-for='bidA'][data-arrow='up']")).not_to_be_disabled()


def test_bid_arrows_cannot_drop_below_minimum(start_game):
    page = start_game("Team Alpha", "Team Beta")
    _finish_round_one(page)

    # Repeatedly press down beyond the floor; value must clamp to 4.
    down_a = page.locator("[data-for='bidA'][data-arrow='down']")
    for _ in range(6):
        down_a.click()
    expect(page.locator("#bidA")).to_have_text("4")
    down_a.click()
    expect(page.locator("#bidA")).to_have_text("4")

    down_b = page.locator("[data-for='bidB'][data-arrow='down']")
    for _ in range(6):
        down_b.click()
    expect(page.locator("#bidB")).to_have_text("4")
    down_b.click()
    expect(page.locator("#bidB")).to_have_text("4")

    expect(page.locator("#unbidNote")).to_have_text("Unbid books left: 5")
