This project is only for keeping scores of games of spades.

Description

This project defines the scoring and gameplay rules for a Spades scorekeeper, customized with special rules.

Setup

At the beginning, ask for team names and player names.

We only track scores at the team level, not per-player.


Input Order Per Hand

1. Ask for bids first (Team A, Team B).

Exception: Round 1 has no bidding, skip directly to books.



2. Ask for books (Team A, Team B).


3. Validate that total books = 13.



Round 1 Special Rules

No bidding.

If a team earns fewer than 4 books, they immediately lose the game.

Otherwise, points are awarded normally with implicit bid = books:

Score = 10 × books for each team.



Rounds 2+

If books ≥ bid: Score = 10 × bid + (books − bid)

If books < bid: Score = −10 × bid  (custom rule: minus 10 per bid book)


Match End

After every hand, print final scores for both teams.

First team to reach 500 points wins.

If both reach 500+ in the same hand, the higher score wins. If tied, continue playing.


Implementation Notes

All calculations must be done in Python.

Immediate-loss check applies only in Round 1.

Books must always sum to 13