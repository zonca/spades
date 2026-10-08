# Spades Scorekeeper

This project is a single-page Spades scorekeeper that helps two teams track bids, books, bags, and the running total for every hand. The UI lives entirely in `index.html`/`script.js`, and persists progress locally so you can reload the page without losing the match. Gameplay and scoring rules are documented in `rules.md`, and the bundled Playwright tests (`uv run pytest`) exercise the UI end to end.

The live app is served at https://zonca.github.io/spades/.

## Getting Started
- Open `index.html` directly in a browser to start a fresh match.
- Enter the four player names (teams are formed from them), pick the winning score, then track bids/books; the app applies the custom rules (blind 10, nil, round-one sudden loss, bag penalties) automatically.
- A saved game is stored in `localStorage` under the key `spades-scorekeeper-state-v1`. Refreshing the page resumes the last match.

## Winning Score
At game start, choose how many points the game is played to:

| Target | Label | Approx. length |
| ------ | ----- | -------------- |
| 200 | quick | ~3 hands |
| 300 | short | ~4–5 hands |
| 500 | standard (default) | ~7–9 hands |

The chosen target is shown on the scoreboard ("to 300"), drives the win check and the "Win at N" line on the score chart, and is saved with the game (`state.targetScore`). Games saved before this option existed resume with 500.

## Testing
- Run the JavaScript unit tests with `npm test` (Node.js 18 or newer).
- Install dependencies with `uv pip install -r requirements.txt`.
- Run the automated browser suite with `uv run pytest`.
- CI (`.github/workflows/ci.yml`) runs both suites on every push and pull request.

## Deployment
GitHub Pages serves the repository root of `main`, so pushing to `main` deploys the app.

## Sync Multiple Devices
In a future iteration you could pipe the snapshot already generated in `script.js` to Firebase Realtime Database so that multiple browsers stay in sync, even as read-only observers.

- **Data model**: Create a `/games/{matchId}` document that stores the JSON payload currently saved to `localStorage` (round, totals, hands, and relevant UI bits like current bids).
- **Write flow**: When the primary scorer submits a hand or updates bids, push the new snapshot via the Firebase JS SDK or the REST API. Only one client needs write permission; all others can connect with read-only rules.
- **Read flow**: Other devices subscribe with `onValue`/`onSnapshot` listeners and simply call the existing `applySnapshot` helper to hydrate the UI, while disabling buttons to keep them in spectator mode.
- **Free-tier limits**: Firebase’s Spark plan is free but capped at 1 GB stored, 10 GB per month download, and roughly 100 simultaneous connections. Realtime Database also enforces write throughput limits, so bursting many updates per second can be throttled. If you exceed the caps, billing switches to the Blaze pay-as-you-go tier (about \$5/GB stored and \$1/GB downloaded).
- **Rule enforcement**: Since `rules.md` asks for Python-based calculations, you could mirror the scoring logic in a lightweight Python service (Cloud Run / Cloud Functions) that validates incoming updates before writing them to Firebase, letting web clients remain thin while keeping the authoritative logic in Python.

With this structure you maintain a single source of truth, observers can follow along live, and you can scale from simple read-only sharing to more sophisticated turn-taking with server-side validation later.
