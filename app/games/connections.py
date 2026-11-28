"""Connections (NYT) — https://www.nytimes.com/games/connections

Example share text:

    Connections
    Puzzle #512
    🟨🟨🟨🟨
    🟩🟦🟩🟩
    🟩🟩🟩🟩
    🟦🟦🟦🟦
    🟪🟪🟪🟪

Every row is one guess. A row with four identical colours is a correct group,
anything else is a mistake. Four mistakes end the game.
Score = number of mistakes (lower is better). The table shows groups found out
of 4, plus the mistakes for solved games: "4/4 · 1✗", "1/4" (lost).
"""

import re

from .base import Game, ParsedResult, normalize, parse_number

HEADER = re.compile(r"Connections\s*\n?\s*Puzzle\s*#\s*([\d.,]+)", re.IGNORECASE)
ROW = re.compile(r"[🟨🟩🟦🟪]{4}")
COLOR_NAMES = {"🟨": "yellow", "🟩": "green", "🟦": "blue", "🟪": "purple"}


class Connections(Game):
    slug = "connections"
    name = "Connections"
    url = "https://www.nytimes.com/games/connections"

    def parse(self, text):
        text = normalize(text)
        match = HEADER.search(text)
        if not match:
            return None
        rows = [line for line in text.split("\n") if ROW.fullmatch(line)]
        correct = [row for row in rows if len(set(row)) == 1]
        mistakes = len(rows) - len(correct)
        return ParsedResult(
            puzzle=parse_number(match.group(1)),
            solved=len(correct) == 4,
            score=mistakes,
            details={
                "grid": rows,
                # The order in which the groups were found, e.g. purple first.
                "order": [COLOR_NAMES[row[0]] for row in correct],
            },
        )

    def summary(self, result):
        # Groups found out of 4, e.g. "1/4" for a lost game with one group.
        # A solved game always has 4/4, so the mistakes are added: "4/4 · 2✗".
        groups = len(result.details.get("order", []))
        if result.solved:
            return f"4/4 · {result.score}✗"
        return f"{groups}/4"
