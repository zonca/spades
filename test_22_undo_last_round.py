import pytest
from playwright.sync_api import expect


def test_undo_is_disabled_before_any_round(start_game):
    page = start_game()
    expect(page.get_by_role("button", name="Undo Last Round")).to_be_disabled()
    expect(page.locator("#unlockBidsBtn")).to_be_hidden()


def test_undo_previous_round_with_current_bids_locked(start_game, play_hand):
    page = start_game()
    play_hand(0, 0, 7, 6)
    play_hand(4, 4, 9, 4)
    play_hand(4, 4, 9, 4)  # Cross the ten-bag penalty threshold.
    assert page.evaluate("state.totalA") == 50
    page.click("#lockBidsBtn")
    page.get_by_role("button", name="Undo Last Round").click()
    expect(page.locator("#pillRound")).to_have_text("Round 3")
    expect(page.locator("#dealerDisplay")).to_have_text("🂡 Dealer: Alex")
    assert page.evaluate("[state.totalA, state.totalB, state.bagsA, state.bagsB]") == [110, 100, 5, 0]
    expect(page.locator("#bidsRow")).to_be_visible()
    expect(page.locator("#unlockBidsBtn")).to_be_hidden()
    expect(page.locator("#handsTable tbody tr")).to_have_count(4)

    page.reload()
    page.click("#resumeBtn")
    assert page.evaluate("[state.totalA, state.bagsA, state.round]") == [110, 5, 3]
    play_hand(4, 4, 4, 9)
    assert page.evaluate("[state.totalA, state.bagsA]") == [150, 5]


@pytest.mark.parametrize("immediate_loss", [False, True])
def test_undo_reopens_finished_game(start_game, play_hand, immediate_loss):
    page = start_game()
    if immediate_loss:
        play_hand(0, 0, 3, 10)
    else:
        page.evaluate("state.targetScore = 200")
        play_hand(0, 0, 7, 6)
        play_hand(10, 4, 10, 3)
        play_hand(10, 4, 10, 3)
    expect(page.locator("#winner")).to_be_visible()

    # Finished games can also be corrected after returning to the app.
    page.reload()
    page.click("#resumeBtn")
    page.get_by_role("button", name="Undo Last Round").click()
    expect(page.locator("#winner")).to_be_hidden()
    assert page.evaluate("state.gameOver") is False
    expect(page.locator("#dealerRow")).to_be_visible()
    expect(page.locator("#submitHandBtn")).to_be_visible()
    expect(page.locator("#pillRound")).to_have_text("Round 1" if immediate_loss else "Round 3")
    if immediate_loss:
        expect(page.get_by_role("button", name="Undo Last Round")).to_be_disabled()
        expect(page.locator("#scorePointsA")).to_have_text("0")
        expect(page.locator("#scorePointsB")).to_have_text("0")
        play_hand(0, 0, 7, 6)
    else:
        assert page.evaluate("[state.totalA, state.totalB]") == [170, 20]
        play_hand(6, 7, 6, 7)
    if immediate_loss:
        expect(page.locator("#winner")).to_be_hidden()
    else:
        expect(page.locator("#winner")).to_be_visible()
