from playwright.sync_api import Page, expect


def test_default_target_is_500(start_game):
    page = start_game()
    expect(page.locator("#targetScoreLabel")).to_have_text("to 500")
    assert page.evaluate("state.targetScore") == 500


def test_short_game_to_200(page: Page, app_url: str, play_hand):
    page.goto(app_url)
    page.fill("#playerA1", "Alice")
    page.fill("#playerA2", "Alex")
    page.fill("#playerB1", "Bob")
    page.fill("#playerB2", "Beth")
    page.click("#targetScoreOptions [data-target='200']")
    expect(page.locator("#targetScoreOptions [data-target='200']")).to_have_attribute("aria-checked", "true")
    expect(page.locator("#targetScoreOptions [data-target='500']")).to_have_attribute("aria-checked", "false")
    page.click("#startBtn")

    expect(page.locator("#targetScoreLabel")).to_have_text("to 200")

    # Round 1: 70 - 60
    page.locator("[data-for='booksA'][data-arrow='up']").click()
    page.click("#submitHandBtn")

    # Round 2: 170 - 20, no winner yet
    play_hand(10, 4, 10, 3)
    expect(page.locator("#winner")).to_be_hidden()

    # Round 3: 270 - -20, Team A passes 200
    play_hand(10, 4, 10, 3)
    expect(page.locator("#winner")).to_be_visible()
    expect(page.locator("#winnerText")).to_have_text("Alice & Alex win!")

    # Target survives a reload of the saved game
    page.reload()
    page.click("#resumeBtn")
    assert page.evaluate("state.targetScore") == 200
    expect(page.locator("#targetScoreLabel")).to_have_text("to 200")
