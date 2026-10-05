import pytest
from playwright.sync_api import expect


@pytest.mark.parametrize("lock_bids", [False, True])
def test_bottom_new_game_restarts_unfinished_saved_match(start_game, lock_bids):
    page = start_game()
    page.locator("[data-for='booksA'][data-arrow='up']").click()
    page.click("#submitHandBtn")
    if lock_bids:
        page.click("#lockBidsBtn")

    # Resume an unfinished match, as when returning to the app later.
    page.reload()
    page.click("#resumeBtn")
    expect(page.locator("#pillRound")).to_have_text("Round 2")
    expect(page.locator("#handsTable tbody tr")).to_have_count(2)
    expect(page.locator("#newGameBtnBottom")).to_be_visible()
    assert page.evaluate("""() => {
        const button = document.querySelector('#newGameBtnBottom');
        return button.getBoundingClientRect().top >=
            document.querySelector('#stats').getBoundingClientRect().bottom;
    }""")

    page.click("#newGameBtnBottom")
    expect(page.locator("#setup")).to_be_visible()
    expect(page.locator("#game")).to_be_hidden()
    expect(page.locator("#resumeBtn")).to_be_hidden()
    assert page.evaluate("localStorage.getItem(STORAGE_KEY)") is None

    page.fill("#playerA1", "Alice")
    page.fill("#playerA2", "Alex")
    page.fill("#playerB1", "Bob")
    page.fill("#playerB2", "Beth")
    page.click("#startBtn")
    expect(page.locator("#pillRound")).to_have_text("Round 1")
    expect(page.locator("#scorePointsA")).to_have_text("0")
    expect(page.locator("#scorePointsB")).to_have_text("0")
    expect(page.locator("#handsTable tbody tr")).to_have_count(0)
    expect(page.locator("#dealerDisplay")).to_have_text("🂡 Dealer: Alice")
