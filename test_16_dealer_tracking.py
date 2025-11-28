from playwright.sync_api import Page, expect
import re


def test_player_name_fields_exist(page: Page, app_url: str):
    """Test that player name input fields are present in setup."""
    page.goto(app_url)
    
    expect(page.locator("#playerA1")).to_be_visible()
    expect(page.locator("#playerA2")).to_be_visible()
    expect(page.locator("#playerB1")).to_be_visible()
    expect(page.locator("#playerB2")).to_be_visible()


def test_dealer_display_visible_on_game_start(start_game):
    """Test that dealer display shows up after starting game."""
    page = start_game()
    
    # Dealer row should be visible
    expect(page.locator("#dealerRow")).to_be_visible()
    expect(page.locator("#dealerDisplay")).to_be_visible()
    # First dealer should be Alice (A1)
    expect(page.locator("#dealerDisplay")).to_contain_text("Dealer: Alice")


def test_dealer_uses_player_names_when_provided(page: Page, app_url: str):
    """Test that dealer display uses actual player names when provided."""
    page.goto(app_url)
    
    # Fill in player names
    page.fill("#playerA1", "Charlie")
    page.fill("#playerA2", "Carol")
    page.fill("#playerB1", "Dave")
    page.fill("#playerB2", "Diana")
    
    page.click("#startBtn")
    
    # First dealer should be Charlie (A1)
    expect(page.locator("#dealerDisplay")).to_have_text("🂡 Dealer: Charlie")


def test_dealer_rotation_across_hands(page: Page, app_url: str):
    """Test that dealer rotates correctly: A1 -> B1 -> A2 -> B2 -> A1..."""
    page.goto(app_url)
    
    # Fill in player names
    page.fill("#playerA1", "Alice")
    page.fill("#playerA2", "Alex")
    page.fill("#playerB1", "Bob")
    page.fill("#playerB2", "Beth")
    
    page.click("#startBtn")
    
    # Round 1: Dealer is Alice (A1)
    expect(page.locator("#dealerDisplay")).to_have_text("🂡 Dealer: Alice")
    
    # Submit Round 1 (no bids in round 1)
    page.locator("[data-for='booksA'][data-arrow='up']").click()  # booksA: 7, booksB: 6
    page.click("#submitHandBtn")
    
    # Round 2: Dealer should be Bob (B1)
    expect(page.locator("#pillRound")).to_have_text("Round 2")
    expect(page.locator("#dealerDisplay")).to_have_text("🂡 Dealer: Bob")
    
    # Submit Round 2 (lock bids, then submit books)
    page.click("#lockBidsBtn")
    page.click("#submitHandBtn")
    
    # Round 3: Dealer should be Alex (A2)
    expect(page.locator("#pillRound")).to_have_text("Round 3")
    expect(page.locator("#dealerDisplay")).to_have_text("🂡 Dealer: Alex")
    
    # Submit Round 3
    page.click("#lockBidsBtn")
    page.click("#submitHandBtn")
    
    # Round 4: Dealer should be Beth (B2)
    expect(page.locator("#pillRound")).to_have_text("Round 4")
    expect(page.locator("#dealerDisplay")).to_have_text("🂡 Dealer: Beth")
    
    # Submit Round 4
    page.click("#lockBidsBtn")
    page.click("#submitHandBtn")
    
    # Round 5: Dealer should rotate back to Alice (A1)
    expect(page.locator("#pillRound")).to_have_text("Round 5")
    expect(page.locator("#dealerDisplay")).to_have_text("🂡 Dealer: Alice")


def test_dealer_shown_in_hands_table(page: Page, app_url: str):
    """Test that dealer name is shown in the hands table for each round."""
    page.goto(app_url)
    
    # Fill in player names
    page.fill("#playerA1", "Alice")
    page.fill("#playerA2", "Alex")
    page.fill("#playerB1", "Bob")
    page.fill("#playerB2", "Beth")
    
    page.click("#startBtn")
    
    # Submit Round 1
    page.locator("[data-for='booksA'][data-arrow='up']").click()
    page.click("#submitHandBtn")
    
    # Check dealer column in table (column 2)
    expect(page.locator("#handsTable tbody tr:nth-child(1) td:nth-child(2)")).to_have_text("Alice")
    
    # Submit Round 2
    page.click("#lockBidsBtn")
    page.click("#submitHandBtn")
    
    # Check dealer for round 2
    expect(page.locator("#handsTable tbody tr:nth-child(2) td:nth-child(2)")).to_have_text("Bob")
    
    # Submit Round 3
    page.click("#lockBidsBtn")
    page.click("#submitHandBtn")
    
    # Check dealer for round 3
    expect(page.locator("#handsTable tbody tr:nth-child(3) td:nth-child(2)")).to_have_text("Alex")
    
    # Submit Round 4
    page.click("#lockBidsBtn")
    page.click("#submitHandBtn")
    
    # Check dealer for round 4
    expect(page.locator("#handsTable tbody tr:nth-child(4) td:nth-child(2)")).to_have_text("Beth")


def test_team_names_derived_from_player_names(page: Page, app_url: str):
    """Test that team names are derived as 'Player1 & Player2'."""
    page.goto(app_url)
    
    # Fill in player names
    page.fill("#playerA1", "Alice")
    page.fill("#playerA2", "Alex")
    page.fill("#playerB1", "Bob")
    page.fill("#playerB2", "Beth")
    
    page.click("#startBtn")
    
    # Team names should be derived from player names
    expect(page.locator("#scoreNameA")).to_have_text("Alice & Alex")
    expect(page.locator("#scoreNameB")).to_have_text("Bob & Beth")


def test_dealer_preserved_after_delete_last_hand(page: Page, app_url: str):
    """Test that deleting last hand correctly restores dealer index."""
    page.goto(app_url)
    
    # Fill in player names
    page.fill("#playerA1", "Alice")
    page.fill("#playerA2", "Alex")
    page.fill("#playerB1", "Bob")
    page.fill("#playerB2", "Beth")
    
    page.click("#startBtn")
    
    # Submit Round 1
    page.locator("[data-for='booksA'][data-arrow='up']").click()
    page.click("#submitHandBtn")
    
    # Round 2: Dealer is Bob
    expect(page.locator("#dealerDisplay")).to_have_text("🂡 Dealer: Bob")
    
    # Submit Round 2
    page.click("#lockBidsBtn")
    page.click("#submitHandBtn")
    
    # Round 3: Dealer is Alex
    expect(page.locator("#dealerDisplay")).to_have_text("🂡 Dealer: Alex")
    
    # Delete last hand (Round 2)
    page.click("#deleteLastBtn")
    
    # Should be back to Round 2, dealer should be Bob
    expect(page.locator("#pillRound")).to_have_text("Round 2")
    expect(page.locator("#dealerDisplay")).to_have_text("🂡 Dealer: Bob")


def test_dealer_shown_in_table_after_delete(page: Page, app_url: str):
    """Test that dealer info in table is preserved after delete."""
    page.goto(app_url)
    
    # Fill in player names
    page.fill("#playerA1", "Alice")
    page.fill("#playerA2", "Alex")
    page.fill("#playerB1", "Bob")
    page.fill("#playerB2", "Beth")
    
    page.click("#startBtn")
    
    # Submit Round 1
    page.locator("[data-for='booksA'][data-arrow='up']").click()
    page.click("#submitHandBtn")
    
    # Submit Round 2
    page.click("#lockBidsBtn")
    page.click("#submitHandBtn")
    
    # Submit Round 3
    page.click("#lockBidsBtn")
    page.click("#submitHandBtn")
    
    # Verify table shows dealers
    expect(page.locator("#handsTable tbody tr:nth-child(1) td:nth-child(2)")).to_have_text("Alice")
    expect(page.locator("#handsTable tbody tr:nth-child(2) td:nth-child(2)")).to_have_text("Bob")
    expect(page.locator("#handsTable tbody tr:nth-child(3) td:nth-child(2)")).to_have_text("Alex")
    
    # Delete last hand
    page.click("#deleteLastBtn")
    
    # Round 1 and 2 should still have correct dealers
    expect(page.locator("#handsTable tbody tr:nth-child(1) td:nth-child(2)")).to_have_text("Alice")
    expect(page.locator("#handsTable tbody tr:nth-child(2) td:nth-child(2)")).to_have_text("Bob")


def test_all_player_names_required(page: Page, app_url: str):
    """Test that all 4 player names are required to start the game."""
    page.goto(app_url)
    
    # Only fill in some player names
    page.fill("#playerA1", "Alice")
    page.fill("#playerB1", "Bob")
    # Leave A2 and B2 empty
    
    page.click("#startBtn")
    
    # Setup should still be visible (game didn't start)
    expect(page.locator("#setup")).to_be_visible()
    expect(page.locator("#setupError")).to_be_visible()


def test_dealer_header_in_table(page: Page, app_url: str):
    """Test that the table header includes Dealer column."""
    page.goto(app_url)
    
    # Fill in all player names
    page.fill("#playerA1", "Alice")
    page.fill("#playerA2", "Alex")
    page.fill("#playerB1", "Bob")
    page.fill("#playerB2", "Beth")
    
    page.click("#startBtn")
    
    # Check that table header has Dealer column (in first row of header)
    expect(page.locator("#handsTable thead tr:first-child th:nth-child(2)")).to_have_text("Dealer")
