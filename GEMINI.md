# Project Overview

This project is a Spades scorekeeper application. It features a web-based user interface (`index.html`) for tracking scores according to a custom set of rules defined in `rules.md`. The project also includes end-to-end tests written in Python using `pytest` and `playwright` to automate browser interactions and verify the UI's functionality.

A notable discrepancy exists: `rules.md` states that "All calculations must be done in Python," however, the core game logic, including scoring, is currently implemented in JavaScript directly within `index.html`.

# Building and Running

## Dependencies

To install the Python dependencies required for testing, use `uv`:

```bash
uv pip install -r requirements.txt
```

## Running Tests

To execute the end-to-end tests using `uv`:

```bash
uv run pytest
```

## Running the Application

The application is a single-page web application. To run it, simply open `index.html` in a web browser. There is no separate server-side component to start.

# Development Conventions

*   **Frontend:** The user interface and game logic are implemented using HTML, CSS, and JavaScript within `index.html`.
*   **Testing:** End-to-end tests are written in Python using the `pytest` framework, leveraging `pytest-playwright` for browser automation.
*   **Game Rules:** The specific rules for scoring and gameplay are documented in `rules.md`.