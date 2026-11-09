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
    assert text.startswith('Alice deals.')
    assert 'round' not in text.lower()
    assert 'Alice and Alex: 0 points.' in text
    assert 'Bob and Beth: 0 points.' in text
    assert 'bid' not in text.lower()
    assert 'books' not in text.lower()
    assert 'bags' not in text
    assert len(text.split()) < 25


def test_status_tracks_bids_books_special_bids_and_resume(start_game, play_hand):
    page = start_game()
    play_hand(0, 0, 7, 6)
    page.click('#nilA')
    page.click('#blind10B')
    text = read_status(page)
    assert text.startswith('Bob deals.')
    assert 'round' not in text.lower()
    assert 'Alice and Alex: 70 points.' in text
    assert 'Bob and Beth: 60 points.' in text
    assert 'bid' not in text.lower()
    assert 'nil' not in text
    assert 'blind' not in text
    assert 'Books entered' not in text
    page.click('#lockBidsBtn')
    page.reload()
    page.click('#resumeBtn')
    text = read_status(page)
    assert 'Bids locked.' in text
    assert 'books' not in text.lower()
    assert 'bid nil.' in text
    assert 'bid blind ten.' in text


def test_finished_status_then_undo(start_game, play_hand):
    page = start_game()
    page.evaluate('state.targetScore = 200')
    play_hand(0, 0, 7, 6)
    play_hand(10, 4, 10, 3)
    play_hand(10, 4, 10, 3)
    text = read_status(page)
    assert 'Alice and Alex win!' in text
    assert 'Dealer' not in text
    assert 'Alice and Alex: 270 points.' in text
    assert 'Bob and Beth: -20 points.' in text
    assert 'books' not in text.lower()
    assert 'bid' not in text.lower()
    assert 'not yet' not in text
    page.click('#undoFinalRoundBtn')
    text = read_status(page)
    assert 'Game over' not in text
    assert 'Alice and Alex: 170 points.' in text
    assert 'bid' not in text.lower()


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
    expect(page.locator('#voiceModeBtn')).to_be_disabled()
    expect(page.locator('#speechStatus')).to_have_text('Reading aloud is unavailable in this browser.')


def latest_speech(page):
    return page.evaluate('window.spoken.at(-1).text')


def test_voice_mode_defaults_off_toggles_and_replaces_speech(start_game):
    page = start_game()
    expect(page.locator('#voiceModeBtn')).to_have_attribute('aria-pressed', 'false')
    page.locator("[data-for='booksA'][data-arrow='up']").click()
    assert page.evaluate('window.spoken.length') == 0
    page.click('#voiceModeBtn')
    assert latest_speech(page) == 'Voice mode on.'
    page.locator("[data-for='booksA'][data-arrow='up']").click()
    assert latest_speech(page) == 'Alice and Alex books 8.'
    assert page.evaluate('window.cancelCount') == 2
    page.click('#voiceModeBtn')
    assert latest_speech(page) == 'Voice mode off.'
    expect(page.locator('#voiceModeBtn')).to_have_attribute('aria-pressed', 'false')
    page.locator("[data-for='booksA'][data-arrow='down']").click()
    assert page.evaluate('window.spoken.length') == 3
    # Finish the off confirmation, then use the manual reader with voice mode off.
    page.evaluate('window.spoken.at(-1).onend()')
    assert read_status(page).startswith('Alice deals.')


def test_voice_confirms_game_actions(page, app_url):
    page.goto(app_url)
    page.click('#voiceModeBtn')
    page.click('#startBtn')
    assert latest_speech(page) == 'Enter all four player names.'
    assert page.evaluate('state.started') is False
    page.click("#targetScoreOptions [data-target='300']")
    assert latest_speech(page) == 'Playing to 300.'
    for field, value in [('playerA1', 'Alice'), ('playerA2', 'Alex'), ('playerB1', 'Bob'), ('playerB2', 'Beth')]:
        page.fill('#' + field, value)
    page.click('#startBtn')
    assert latest_speech(page) == 'Playing to 300. Alice deals.'
    page.click('#submitHandBtn')
    assert latest_speech(page) == 'Saved. Alice and Alex: 60 points. Bob and Beth: 70 points.'
    page.locator("[data-for='bidA'][data-arrow='up']").click()
    assert latest_speech(page) == 'Alice and Alex bid 7.'
    page.click('#nilA')
    assert latest_speech(page) == 'Alice and Alex bid nil.'
    page.click('#nilA')
    assert latest_speech(page) == 'Alice and Alex bid 7.'
    page.click('#blind10B')
    assert latest_speech(page) == 'Bob and Beth bid blind ten.'
    page.click('#blind10B')
    assert latest_speech(page) == f"Bob and Beth bid {page.locator('#bidB').inner_text()}."
    page.click('#lockBidsBtn')
    assert latest_speech(page) == f"Bids locked. Alice and Alex bid 7. Bob and Beth bid {page.locator('#bidB').inner_text()}."
    page.click('#deleteLastBtn')
    assert latest_speech(page).startswith('Bids unlocked.')
    page.click('#deleteLastBtn')
    assert latest_speech(page) == 'Last round undone.'


def test_voice_confirms_finish_undo_reset_and_remembers_mode(start_game, play_hand):
    page = start_game()
    page.click('#voiceModeBtn')
    play_hand(0, 0, 3, 10)
    assert latest_speech(page).startswith('Bob and Beth win!')
    page.click('#undoFinalRoundBtn')
    assert latest_speech(page) == 'Last round undone.'
    page.reload()
    expect(page.locator('#voiceModeBtn')).to_have_attribute('aria-pressed', 'true')
    assert page.evaluate('window.spoken.length') == 0  # No unsolicited speech on load.
    page.click('#resumeBtn')
    assert latest_speech(page) == 'Game resumed. Alice deals.'
    page.click('#newGameBtnBottom')
    expect(page.locator('#setup')).to_be_visible()
    expect(page.locator('#game')).to_be_hidden()
    expect(page.locator('#newGameBtnBottom')).to_be_hidden()
    assert latest_speech(page) == 'New game.'
    assert page.evaluate('localStorage.getItem(STORAGE_KEY)') is None
    assert page.evaluate('localStorage.getItem(VOICE_MODE_KEY)') == 'true'
    # Resetting a game preserves the voice preference and leaves speech running.
    expect(page.locator('#voiceModeBtn')).to_have_attribute('aria-pressed', 'true')
    page.reload()
    expect(page.locator('#voiceModeBtn')).to_have_attribute('aria-pressed', 'true')
    assert page.evaluate('window.spoken.length') == 0


def test_spinner_limit_does_not_confirm_a_change(start_game):
    page = start_game()
    page.click('#voiceModeBtn')
    for _ in range(7):
        page.locator("[data-for='booksA'][data-arrow='up']").click()
    count = page.evaluate('window.spoken.length')
    page.locator("[data-for='booksA'][data-arrow='up']").click()
    assert page.evaluate('window.spoken.length') == count
    expect(page.locator('#booksA')).to_have_text('13')


def test_lock_confirmation_names_special_bids(start_game, play_hand):
    page = start_game()
    play_hand(0, 0, 7, 6)
    page.click('#nilA')
    page.click('#blind10B')
    page.click('#voiceModeBtn')
    page.click('#lockBidsBtn')
    assert latest_speech(page) == 'Bids locked. Alice and Alex bid nil. Bob and Beth bid blind ten.'
