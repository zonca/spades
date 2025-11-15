from playwright.sync_api import expect


def _play_round_one(page) -> None:
    """Helper to finish round one with a 7 / 6 split."""
    page.locator("[data-for='booksA'][data-arrow='up']").click()
    expect(page.locator("#booksA")).to_have_text("7")
    expect(page.locator("#booksB")).to_have_text("6")
    page.click("#submitHandBtn")
    expect(page.locator("#pillRound")).to_have_text("Round 2")


def test_nil_success_awards_bonus(start_game):
    page = start_game("Team Alpha", "Team Beta")
    _play_round_one(page)

    # Round 2 bidding: Team Alpha declares Nil, bids 5 vs 8.
    page.locator("[data-for='bidA'][data-arrow='down']").click()  # 6 -> 5
    page.locator("[data-for='bidB'][data-arrow='up']").click()  # 6 -> 7
    page.locator("[data-for='bidB'][data-arrow='up']").click()  # 7 -> 8
    page.click("#nilA")
    expect(page.locator("#nilA")).to_have_text("Nil ✓")

    page.click("#lockBidsBtn")

    # Set books so Team Alpha makes Nil and Team Beta takes all 13.
    for _ in range(6):
        page.locator("[data-for='booksA'][data-arrow='down']").click()
    expect(page.locator("#booksA")).to_have_text("0")
    expect(page.locator("#booksB")).to_have_text("13")

    page.click("#submitHandBtn")

    expect(page.locator("#pillRound")).to_have_text("Round 3")
    # Verify Nil bonus applied.
    # Team A: Nil made (0 books) = +100
    # Team B: bid 8, made 13 = 10*8 = 80 (5 sandbags not counted in score)
    expect(page.locator("#handsTable tbody tr:nth-child(2) td:nth-child(4)")).to_have_text("100")
    expect(page.locator("#handsTable tbody tr:nth-child(2) td:nth-child(5)")).to_have_text("80")
    expect(page.locator("#handsTable tbody tr:nth-child(2) td:nth-child(6)")).to_have_text("170")
    expect(page.locator("#handsTable tbody tr:nth-child(2) td:nth-child(7)")).to_have_text("140 (5)")
    expect(page.locator("#pillA")).to_have_text("Team Alpha: 170")
    expect(page.locator("#pillB")).to_have_text("Team Beta: 140")
    expect(page.locator("#nilA")).to_have_text("Nil")


def test_nil_failure_applies_penalty(start_game):
    page = start_game("Team Alpha", "Team Beta")
    _play_round_one(page)

    # Round 2 bidding: Team Beta declares Nil, bids stay 6 / 7.
    page.locator("[data-for='bidB'][data-arrow='up']").click()  # 6 -> 7
    page.click("#nilB")
    expect(page.locator("#nilB")).to_have_text("Nil ✓")

    page.click("#lockBidsBtn")

    # Books: Team Alpha 5, Team Beta 8 (Nil fails).
    page.locator("[data-for='booksA'][data-arrow='down']").click()  # 6 -> 5
    expect(page.locator("#booksA")).to_have_text("5")
    expect(page.locator("#booksB")).to_have_text("8")

    page.click("#submitHandBtn")

    expect(page.locator("#pillRound")).to_have_text("Round 3")
    # Team A: bid 6, made 5 = -10*6 = -60
    # Team B: bid Nil (0), made 8 = -100 for failing Nil, plus 8 sandbags (not counted in score)
    expect(page.locator("#handsTable tbody tr:nth-child(2) td:nth-child(4)")).to_have_text("-60")
    expect(page.locator("#handsTable tbody tr:nth-child(2) td:nth-child(5)")).to_have_text("-100")
    expect(page.locator("#handsTable tbody tr:nth-child(2) td:nth-child(6)")).to_have_text("10")
    expect(page.locator("#handsTable tbody tr:nth-child(2) td:nth-child(7)")).to_have_text("-40 (8)")
    expect(page.locator("#pillA")).to_have_text("Team Alpha: 10")
    expect(page.locator("#pillB")).to_have_text("Team Beta: -40")
    expect(page.locator("#nilB")).to_have_text("Nil")
