from playwright.sync_api import Page, expect


def test_start_game_with_player_names(page: Page, app_url: str):
    page.goto(app_url)

    # Fill in all 4 player names
    page.fill("#playerA1", "Alice")
    page.fill("#playerA2", "Alex")
    page.fill("#playerB1", "Bob")
    page.fill("#playerB2", "Beth")

    # Click the Start Game button
    page.click("#startBtn")

    # Assert that "Round 1" is visible on the next page
    expect(page.locator("#pillRound")).to_have_text("Round 1")
    
    # Check team names are derived from player names with Team A/B labels
    expect(page.locator("#scoreNameA")).to_have_text("Team A: Alice & Alex")
    expect(page.locator("#scoreNameB")).to_have_text("Team B: Bob & Beth")
