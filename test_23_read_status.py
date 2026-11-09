import pytest
from playwright.sync_api import expect


@pytest.fixture(autouse=True)
def speech_stub(page):
    # Verify the browser integration without depending on installed audio voices.
    page.add_init_script("""(() => {
        window.spoken = [];
        window.cancelCount = 0;
        Object.defineProperty(window, 'speechSynthesis', {value: {
            speak(utterance) { window.spoken.push(utterance); },
            cancel() { window.cancelCount++; },
        }, configurable: true});
        window.SpeechSynthesisUtterance = class {
            constructor(text) { this.text = text; }
        };
    })();""")


def read_status(page):
    page.get_by_role('button', name='Read Game Status Aloud').click()
    text = page.evaluate('window.spoken.at(-1).text')
    page.evaluate('window.spoken.at(-1).onend()')
    return text


def test_first_round_status_and_mobile_button(start_game):
    page = start_game()
    page.set_viewport_size({'width': 375, 'height': 812})
    box = page.locator('#readStatusBtn').bounding_box()
    assert box['x'] >= 0 and box['x'] + box['width'] <= 375
    text = read_status(page)
    assert 'Round 1. Dealer: Alice.' in text
    assert 'Playing to 500 points.' in text
    assert 'Alice and Alex: 0 points, 0 bags.' in text
    assert 'Bob and Beth: 0 points, 0 bags.' in text
    assert 'First round: no bids.' in text
    assert 'not yet submitted: Alice and Alex, 6; Bob and Beth, 7.' in text


def test_status_tracks_bids_books_special_bids_and_resume(start_game, play_hand):
    page = start_game()
    play_hand(0, 0, 7, 6)
    page.click('#nilA')
    page.click('#blind10B')
    text = read_status(page)
    assert 'Dealer: Bob.' in text
    assert 'Alice and Alex: 70 points, 0 bags.' in text
    assert 'Bob and Beth: 60 points, 0 bags.' in text
    assert 'Bids being entered, not yet locked.' in text
    assert 'Alice and Alex bid nil.' in text
    assert 'Bob and Beth bid blind ten.' in text
    assert 'Books entered' not in text
    page.click('#lockBidsBtn')
    page.reload()
    page.click('#resumeBtn')
    text = read_status(page)
    assert 'Bids locked.' in text
    assert 'not yet submitted:' in text
    assert 'bid nil.' in text
    assert 'bid blind ten.' in text


def test_finished_status_then_undo(start_game, play_hand):
    page = start_game()
    page.evaluate('state.targetScore = 200')
    play_hand(0, 0, 7, 6)
    play_hand(10, 4, 10, 3)
    play_hand(10, 4, 10, 3)
    text = read_status(page)
    assert 'Game over. Alice and Alex win!' in text
    assert 'Final round 3. Dealer: Alex.' in text
    assert 'Alice and Alex: 270 points, 0 bags.' in text
    assert 'Bob and Beth: -20 points, 0 bags.' in text
    assert 'Final round books: Alice and Alex, 10; Bob and Beth, 3.' in text
    assert 'not yet' not in text
    page.click('#undoFinalRoundBtn')
    text = read_status(page)
    assert 'Game over' not in text
    assert 'Alice and Alex: 170 points, 0 bags.' in text
    assert 'Bids being entered' in text


def test_stop_retry_and_speech_failure(start_game):
    page = start_game()
    page.click('#readStatusBtn')
    expect(page.locator('#readStatusBtn')).to_have_text('Stop Reading')
    page.click('#readStatusBtn')
    assert page.evaluate('window.cancelCount') == 2
    page.click('#readStatusBtn')
    # A delayed event from the stopped reading must not reset the new one.
    page.evaluate('window.spoken[0].onend()')
    expect(page.locator('#readStatusBtn')).to_have_text('Stop Reading')
    page.evaluate("window.spoken[1].onerror({error: 'voice-unavailable'})")
    expect(page.locator('#readStatusBtn')).to_have_text('Read Game Status Aloud')
    expect(page.locator('#speechStatus')).to_contain_text('Could not read aloud')
    read_status(page)
    expect(page.locator('#speechStatus')).to_be_hidden()


def test_unsupported_browser_explains_disabled_button(page, app_url):
    page.add_init_script("Object.defineProperty(window, 'speechSynthesis', {value: undefined})")
    page.goto(app_url)
    assert page.locator('#readStatusBtn').is_disabled()
    expect(page.locator('#speechStatus')).to_have_text('Reading aloud is unavailable in this browser.')
