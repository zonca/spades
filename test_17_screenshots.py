"""
Screenshot tests for dealer tracking feature.
These tests take screenshots of various states in the dealer tracking feature.
"""
from playwright.sync_api import Page


def test_screenshot_setup_with_player_fields(page: Page, app_url: str):
    """Take screenshot of setup page with player name fields."""
    page.goto(app_url)
    page.set_viewport_size({"width": 480, "height": 800})
    
    # Fill in player names
    page.fill("#playerA1", "Alice")
    page.fill("#playerA2", "Alex")
    page.fill("#playerB1", "Bob")
    page.fill("#playerB2", "Beth")
    
    page.screenshot(path="screenshots/01_setup_with_player_names.png", full_page=True)


def test_screenshot_dealer_display_round1(page: Page, app_url: str):
    """Take screenshot of Round 1 showing dealer display."""
    page.goto(app_url)
    page.set_viewport_size({"width": 480, "height": 800})
    
    # Fill in player names
    page.fill("#playerA1", "Alice")
    page.fill("#playerA2", "Alex")
    page.fill("#playerB1", "Bob")
    page.fill("#playerB2", "Beth")
    
    page.click("#startBtn")
    
    page.screenshot(path="screenshots/02_round1_dealer_alice.png", full_page=True)


def test_screenshot_dealer_rotation(page: Page, app_url: str):
    """Take screenshots showing dealer rotation through multiple rounds."""
    page.goto(app_url)
    page.set_viewport_size({"width": 480, "height": 900})
    
    # Fill in player names
    page.fill("#playerA1", "Alice")
    page.fill("#playerA2", "Alex")
    page.fill("#playerB1", "Bob")
    page.fill("#playerB2", "Beth")
    
    page.click("#startBtn")
    
    # Round 1: Alice
    page.locator("[data-for='booksA'][data-arrow='up']").click()
    page.click("#submitHandBtn")
    
    # Round 2: Bob
    page.screenshot(path="screenshots/03_round2_dealer_bob.png", full_page=True)
    
    page.click("#lockBidsBtn")
    page.click("#submitHandBtn")
    
    # Round 3: Alex
    page.screenshot(path="screenshots/04_round3_dealer_alex.png", full_page=True)
    
    page.click("#lockBidsBtn")
    page.click("#submitHandBtn")
    
    # Round 4: Beth
    page.screenshot(path="screenshots/05_round4_dealer_beth.png", full_page=True)
    
    page.click("#lockBidsBtn")
    page.click("#submitHandBtn")
    
    # Round 5: Back to Alice
    page.screenshot(path="screenshots/06_round5_dealer_alice_again.png", full_page=True)


def test_screenshot_hands_table_with_dealers(page: Page, app_url: str):
    """Take screenshot showing dealer column in hands table."""
    page.goto(app_url)
    page.set_viewport_size({"width": 480, "height": 1200})
    
    # Fill in player names
    page.fill("#playerA1", "Alice")
    page.fill("#playerA2", "Alex")
    page.fill("#playerB1", "Bob")
    page.fill("#playerB2", "Beth")
    
    page.click("#startBtn")
    
    # Play several rounds
    # Round 1
    page.locator("[data-for='booksA'][data-arrow='up']").click()
    page.click("#submitHandBtn")
    
    # Round 2
    page.click("#lockBidsBtn")
    page.click("#submitHandBtn")
    
    # Round 3
    page.click("#lockBidsBtn")
    page.click("#submitHandBtn")
    
    # Round 4
    page.click("#lockBidsBtn")
    page.click("#submitHandBtn")
    
    # Take screenshot focused on hands table showing dealer rotation
    page.screenshot(path="screenshots/07_hands_table_with_dealers.png", full_page=True)
