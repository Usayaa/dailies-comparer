"""krillion.io — https://krillion.io

Example share text:

    Krillion #134 🦐
    330

    🏮🐟🦑🐟🫧🏮🐟

Line 1: puzzle number. Line 2: the score (points, higher is better).
The emoji line shows the value of each of the seven answers; it is stored in
`details` but not used yet.
"""

import re

from .base import Game, ParsedResult, normalize, parse_number

HEADER = re.compile(r"Krillion\s*#\s*([\d.,]+)", re.IGNORECASE)
# The score is the only line consisting of nothing but a number.
SCORE = re.compile(r"^([\d.,]+)$", re.MULTILINE)


class Krillion(Game):
    slug = "krillion"
    name = "krillion"
    url = "https://krillion.io"
    lower_is_better = False  # points: more is better

    def parse(self, text):
        text = normalize(text)
        match = HEADER.search(text)
        score = SCORE.search(text)
        if not match or not score:
            return None
        # The last non-empty line holds the seven answer emojis.
        lines = [line for line in text.split("\n") if line]
        return ParsedResult(
            puzzle=parse_number(match.group(1)),
            solved=True,
            score=parse_number(score.group(1)),
            details={"answers": lines[-1] if len(lines) > 2 else ""},
        )

    def summary(self, result):
        return str(result.score)

    def bucket(self, score):
        # Scores vary a lot, so group the stats distribution in steps of 100.
        return score // 100 * 100

    def bucket_label(self, bucket):
        return f"{bucket}+"
