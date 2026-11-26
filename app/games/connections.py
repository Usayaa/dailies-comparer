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
Score = number of mistakes (lower is better).
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
        # Mistakes out of the 4 allowed; "4/4 ✗" therefore means lost.
        return f"{result.score}/4 ✗"
