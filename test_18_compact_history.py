"""
Tests for compact history table layout with color coding.
- Red (books-set class): team was set (books < bid)
- Blue (books-made class): bid equals result (books = bid)
"""
from playwright.sync_api import Page, expect


def test_compact_history_layout(start_game, play_hand):
    """Test that the compact history table has proper structure with A:/B: rows."""
    page = start_game()

    # Round 1 (no bids, books only)
    page.locator("[data-for='booksA'][data-arrow='up']").click()  # booksA: 7, booksB: 6
    page.click("#submitHandBtn")

    # Verify the new table structure has Team column
    expect(page.locator("#handsTable thead th")).to_have_count(6)
    expect(page.locator("#handsTable thead th:nth-child(3)")).to_have_text("Team")

    # Verify each round has two rows (A: and B:)
    expect(page.locator("#handsTable tbody tr")).to_have_count(2)
    expect(page.locator("#handsTable tbody tr:nth-child(1) td:nth-child(3)")).to_have_text("A:")
    expect(page.locator("#handsTable tbody tr:nth-child(2) td:nth-child(1)")).to_have_text("B:")


def test_books_made_blue_color(start_game, play_hand):
    """Test that Books (bid) is blue when bid equals result."""
    page = start_game()

    # Round 1
    page.locator("[data-for='booksA'][data-arrow='up']").click()
    page.click("#submitHandBtn")

    # Round 2: Team A bids 6, makes exactly 6 books
    play_hand(6, 6, 6, 7)

    # Team A should have blue color (books-made class) since 6 = 6
    books_cell_a = page.locator("#handsTable tbody tr:nth-child(3) td:nth-child(4)")
    expect(books_cell_a).to_have_class("books-made")
    expect(books_cell_a).to_have_text("6 (6)")


def test_books_set_red_color(start_game, play_hand):
    """Test that Books (bid) is red when team was set (books < bid)."""
    page = start_game()

    # Round 1
    page.locator("[data-for='booksA'][data-arrow='up']").click()
    page.click("#submitHandBtn")

    # Round 2: Team A bids 6, makes only 4 books (set!)
    play_hand(6, 6, 4, 9)

    # Team A should have red color (books-set class) since 4 < 6
    books_cell_a = page.locator("#handsTable tbody tr:nth-child(3) td:nth-child(4)")
    expect(books_cell_a).to_have_class("books-set")
    expect(books_cell_a).to_have_text("4 (6)")


def test_books_over_bid_no_color(start_game, play_hand):
    """Test that Books (bid) has no special color when books > bid (overbid/bags)."""
    page = start_game()

    # Round 1
    page.locator("[data-for='booksA'][data-arrow='up']").click()
    page.click("#submitHandBtn")

    # Round 2: Team A bids 6, makes 8 books (2 bags, but made bid)
    play_hand(6, 6, 8, 5)

    # Team A should have no special class since 8 > 6 (overbid, not set or exact)
    books_cell_a = page.locator("#handsTable tbody tr:nth-child(3) td:nth-child(4)")
    expect(books_cell_a).not_to_have_class("books-set")
    expect(books_cell_a).not_to_have_class("books-made")
    expect(books_cell_a).to_have_text("8 (6)")


def test_round1_no_color(start_game):
    """Test that Round 1 has no color since there's no bid."""
    page = start_game()

    # Round 1
    page.locator("[data-for='booksA'][data-arrow='up']").click()
    page.click("#submitHandBtn")

    # Round 1 should have no color classes since bid is "-"
    books_cell_a = page.locator("#handsTable tbody tr:nth-child(1) td:nth-child(4)")
    expect(books_cell_a).not_to_have_class("books-set")
    expect(books_cell_a).not_to_have_class("books-made")
    expect(books_cell_a).to_have_text("7 (-)")


def test_screenshot_compact_history_with_colors(page: Page, app_url: str):
    """Take screenshot showing compact history with color coding."""
    page.goto(app_url)
    page.set_viewport_size({"width": 480, "height": 1400})
    
    # Fill in player names
    page.fill("#playerA1", "Alice")
    page.fill("#playerA2", "Alex")
    page.fill("#playerB1", "Bob")
    page.fill("#playerB2", "Beth")
    
    page.click("#startBtn")
    
    # Round 1: No bids
    page.locator("[data-for='booksA'][data-arrow='up']").click()  # A:7, B:6
    page.click("#submitHandBtn")
    
    # Round 2: A bids 6, makes 6 (blue - exact), B bids 6, makes 7 (no color - over)
    page.click("#lockBidsBtn")
    page.locator("[data-for='booksA'][data-arrow='down']").click()  # A:6, B:7
    page.click("#submitHandBtn")
    
    # Round 3: A bids 6, makes 4 (red - set), B bids 6, makes 9 (no color - over)
    page.click("#lockBidsBtn")
    page.locator("[data-for='booksA'][data-arrow='down']").click()
    page.locator("[data-for='booksA'][data-arrow='down']").click()  # A:4, B:9
    page.click("#submitHandBtn")
    
    # Round 4: Both teams make exact bid (both blue)
    page.click("#lockBidsBtn")
    page.click("#submitHandBtn")  # A:6, B:7
    
    page.screenshot(path="screenshots/08_compact_history_with_colors.png", full_page=True)
