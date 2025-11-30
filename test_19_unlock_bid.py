from playwright.sync_api import expect


def test_unlock_bid_button_appears_when_bids_locked(start_game, play_hand):
    """Test that the delete button shows 'Unlock Bid' when bids are locked."""
    page = start_game()

    # Round 1 - Submit a hand
    expect(page.locator("#pillRound")).to_have_text("Round 1")
    page.locator("[data-for='booksA'][data-arrow='up']").click()  # booksA: 7, booksB: 6
    page.click("#submitHandBtn")
    expect(page.locator("#pillA")).to_have_text("Alice & Alex: 70")
    expect(page.locator("#pillB")).to_have_text("Bob & Beth: 60")

    # Round 2 - Lock bids
    expect(page.locator("#pillRound")).to_have_text("Round 2")
    expect(page.locator("#deleteLastBtn")).to_have_text("Delete Last Hand")
    
    # Lock the bids
    page.click("#lockBidsBtn")
    expect(page.locator("#status")).to_have_text("Bids locked. Now set books.")
    
    # The button should now say "Unlock Bid"
    expect(page.locator("#deleteLastBtn")).to_have_text("Unlock Bid")


def test_unlock_bid_restores_bid_phase(start_game, play_hand):
    """Test that clicking 'Unlock Bid' restores the bid phase."""
    page = start_game()

    # Round 1 - Submit a hand
    page.locator("[data-for='booksA'][data-arrow='up']").click()  # booksA: 7, booksB: 6
    page.click("#submitHandBtn")

    # Round 2 - Lock bids
    expect(page.locator("#pillRound")).to_have_text("Round 2")
    
    # Set specific bids before locking
    page.locator("[data-for='bidA'][data-arrow='up']").click()  # bidA: 7
    page.locator("[data-for='bidB'][data-arrow='up']").click()  # bidB: 7
    expect(page.locator("#bidA")).to_have_text("7")
    expect(page.locator("#bidB")).to_have_text("7")
    
    # Lock the bids
    page.click("#lockBidsBtn")
    expect(page.locator("#status")).to_have_text("Bids locked. Now set books.")
    expect(page.locator("#booksRow")).to_be_visible()
    
    # Click "Unlock Bid"
    page.click("#deleteLastBtn")
    expect(page.locator("#status")).to_have_text("Bids unlocked.")
    
    # Verify bids are unlocked
    expect(page.locator("#deleteLastBtn")).to_have_text("Delete Last Hand")
    expect(page.locator("#lockBidsBtn")).to_be_visible()
    expect(page.locator("#unbidNote")).to_be_visible()
    
    # Verify bid values are preserved
    expect(page.locator("#bidA")).to_have_text("7")
    expect(page.locator("#bidB")).to_have_text("7")


def test_unlock_bid_does_not_delete_hand(start_game, play_hand):
    """Test that clicking 'Unlock Bid' does not delete the previous hand."""
    page = start_game()

    # Round 1 - Submit a hand
    page.locator("[data-for='booksA'][data-arrow='up']").click()  # booksA: 7, booksB: 6
    page.click("#submitHandBtn")
    expect(page.locator("#pillA")).to_have_text("Alice & Alex: 70")
    expect(page.locator("#pillB")).to_have_text("Bob & Beth: 60")

    # Round 2 - Lock bids
    expect(page.locator("#pillRound")).to_have_text("Round 2")
    page.click("#lockBidsBtn")
    
    # Click "Unlock Bid"
    page.click("#deleteLastBtn")
    
    # Scores should remain the same (hand was not deleted)
    expect(page.locator("#pillA")).to_have_text("Alice & Alex: 70")
    expect(page.locator("#pillB")).to_have_text("Bob & Beth: 60")
    expect(page.locator("#pillRound")).to_have_text("Round 2")


def test_can_continue_after_unlock_bid(start_game, play_hand):
    """Test that the game can continue after unlocking bids."""
    page = start_game()

    # Round 1 - Submit a hand
    page.locator("[data-for='booksA'][data-arrow='up']").click()  # booksA: 7, booksB: 6
    page.click("#submitHandBtn")

    # Round 2 - Lock bids, then unlock
    page.click("#lockBidsBtn")
    page.click("#deleteLastBtn")  # Unlock bid
    
    # Now play round 2 normally
    play_hand(6, 7, 6, 7)
    expect(page.locator("#pillA")).to_have_text("Alice & Alex: 130")
    expect(page.locator("#pillB")).to_have_text("Bob & Beth: 130")
    expect(page.locator("#pillRound")).to_have_text("Round 3")
