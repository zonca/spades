from playwright.sync_api import expect


def test_team_labels_in_top_summary_scoreboard(start_game):
    """Test that Team A and Team B labels appear in the top summary scoreboard."""
    page = start_game()

    # Check that Team A label appears with player names
    expect(page.locator("#scoreNameA")).to_have_text("Team A: Alice & Alex")
    
    # Check that Team B label appears with player names
    expect(page.locator("#scoreNameB")).to_have_text("Team B: Bob & Beth")


def test_team_labels_with_custom_player_names(start_game):
    """Test team labels work with different player names."""
    page = start_game(
        player_a1="John",
        player_a2="Jane",
        player_b1="Mike",
        player_b2="Mary"
    )

    # Check that Team A label appears with custom player names
    expect(page.locator("#scoreNameA")).to_have_text("Team A: John & Jane")
    
    # Check that Team B label appears with custom player names
    expect(page.locator("#scoreNameB")).to_have_text("Team B: Mike & Mary")


def test_team_labels_persist_across_rounds(start_game, play_hand):
    """Test that team labels persist in the top summary after playing rounds."""
    page = start_game()

    # Play Round 1
    expect(page.locator("#pillRound")).to_have_text("Round 1")
    page.locator("[data-for='booksA'][data-arrow='up']").click()  # booksA: 7, booksB: 6
    page.click("#submitHandBtn")

    # Check team labels still show correctly after round 1
    expect(page.locator("#scoreNameA")).to_have_text("Team A: Alice & Alex")
    expect(page.locator("#scoreNameB")).to_have_text("Team B: Bob & Beth")

    # Play Round 2
    expect(page.locator("#pillRound")).to_have_text("Round 2")
    play_hand(6, 6, 6, 7)

    # Check team labels still show correctly after round 2
    expect(page.locator("#scoreNameA")).to_have_text("Team A: Alice & Alex")
    expect(page.locator("#scoreNameB")).to_have_text("Team B: Bob & Beth")
