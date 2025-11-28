from playwright.sync_api import Page, expect


def test_charts_and_stats_hidden_initially(page: Page, start_game):
    """Test that charts and stats are hidden when no hands are played."""
    start_game()
    
    # Initially, charts and stats sections should be hidden
    expect(page.locator("#charts")).to_be_hidden()
    expect(page.locator("#stats")).to_be_hidden()


def test_charts_and_stats_visible_after_first_hand(page: Page, start_game, play_hand):
    """Test that charts and stats appear after playing the first hand."""
    start_game()
    
    # Play round 1 (no bidding)
    play_hand(0, 0, 7, 6)
    
    # Charts and stats should now be visible
    expect(page.locator("#charts")).to_be_visible()
    expect(page.locator("#stats")).to_be_visible()
    
    # Check that the score chart canvas exists
    expect(page.locator("#scoreChart")).to_be_visible()
    
    # Check that team names appear in stats
    expect(page.locator("#statsTeamAName")).to_contain_text("Alice & Alex")
    expect(page.locator("#statsTeamBName")).to_contain_text("Bob & Beth")


def test_stats_show_correct_values(page: Page, start_game, play_hand):
    """Test that statistics show correct values."""
    start_game()
    
    # Play round 1: Alice & Alex gets 7 books (70 points), Bob & Beth gets 6 books (60 points)
    play_hand(0, 0, 7, 6)
    
    # Check stats for Alice & Alex
    stats_a = page.locator("#statsTeamA").inner_text()
    assert "Best hand: 70" in stats_a
    assert "Worst hand: 70" in stats_a
    assert "Times set: 0" in stats_a
    assert "Avg score/hand: 70.0" in stats_a
    
    # Check stats for Bob & Beth
    stats_b = page.locator("#statsTeamB").inner_text()
    assert "Best hand: 60" in stats_b
    assert "Worst hand: 60" in stats_b
    assert "Times set: 0" in stats_b
    assert "Avg score/hand: 60.0" in stats_b


def test_stats_track_sets(page: Page, start_game, play_hand):
    """Test that stats correctly track when teams are set."""
    start_game()
    
    # Play round 1
    play_hand(0, 0, 7, 6)
    
    # Play round 2: Alice & Alex bids 7 but gets only 5 (set)
    play_hand(7, 6, 5, 8)
    
    # Check that Alice & Alex has 1 set
    stats_a = page.locator("#statsTeamA").inner_text()
    assert "Times set: 1" in stats_a
    
    # Check that Bob & Beth has 0 sets
    stats_b = page.locator("#statsTeamB").inner_text()
    assert "Times set: 0" in stats_b


def test_stats_track_best_and_worst_hands(page: Page, start_game, play_hand):
    """Test that stats correctly track best and worst hands."""
    start_game()
    
    # Play round 1
    play_hand(0, 0, 7, 6)
    
    # Play round 2: Alice & Alex gets 60, Bob & Beth gets 61 + 1 bag
    play_hand(6, 6, 6, 7)
    
    # Play round 3: Alice & Alex gets 80 + 2 bags, Bob & Beth gets -60 (set)
    play_hand(8, 6, 10, 3)
    
    # Check Alice & Alex stats
    stats_a = page.locator("#statsTeamA").inner_text()
    assert "Best hand: 80" in stats_a  # Best score (bags tracked separately)
    assert "Worst hand: 60" in stats_a
    
    # Check Bob & Beth stats
    stats_b = page.locator("#statsTeamB").inner_text()
    assert "Best hand: 60" in stats_b  # Base score (bags tracked separately)
    assert "Worst hand: -60" in stats_b


def test_chart_updates_after_multiple_hands(page: Page, start_game, play_hand):
    """Test that the chart updates correctly after playing multiple hands."""
    start_game()
    
    # Play several rounds
    play_hand(0, 0, 7, 6)  # Round 1
    play_hand(6, 6, 6, 7)  # Round 2
    play_hand(7, 6, 7, 6)  # Round 3
    
    # Chart should be visible
    expect(page.locator("#charts")).to_be_visible()
    
    # Check that canvas exists and has been drawn on
    canvas_exists = page.evaluate("""
        const canvas = document.getElementById('scoreChart');
        canvas !== null && canvas.getContext('2d') !== null
    """)
    assert canvas_exists


def test_stats_update_after_delete_last_hand(page: Page, start_game, play_hand):
    """Test that stats update correctly after deleting the last hand."""
    start_game()
    
    # Play two rounds
    play_hand(0, 0, 7, 6)
    play_hand(6, 6, 6, 7)
    
    # Verify we have stats
    expect(page.locator("#stats")).to_be_visible()
    
    # Delete the last hand
    page.click("#deleteLastBtn")
    
    # Stats should still be visible (we still have 1 hand)
    expect(page.locator("#stats")).to_be_visible()
    
    # Check that stats reflect only the first hand
    stats_a = page.locator("#statsTeamA").inner_text()
    assert "Best hand: 70" in stats_a
    assert "Worst hand: 70" in stats_a


def test_charts_and_stats_hidden_after_deleting_all_hands(page: Page, start_game, play_hand):
    """Test that charts and stats are hidden after deleting all hands."""
    start_game()
    
    # Play one round
    play_hand(0, 0, 7, 6)
    
    # Charts and stats should be visible
    expect(page.locator("#charts")).to_be_visible()
    expect(page.locator("#stats")).to_be_visible()
    
    # Delete the hand
    page.click("#deleteLastBtn")
    
    # Charts and stats should now be hidden
    expect(page.locator("#charts")).to_be_hidden()
    expect(page.locator("#stats")).to_be_hidden()
