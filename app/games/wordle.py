"""Wordle (NYT) — https://www.nytimes.com/games/wordle

Example share text:

    Wordle 1,621 4/6*

    ⬛🟨⬛⬛⬛
    🟩🟩⬛🟨⬛
    🟩🟩🟩🟨⬛
    🟩🟩🟩🟩🟩

"X/6" means not solved; a trailing "*" means hard mode.
Score = number of guesses (lower is better).
"""

import re

from .base import Game, ParsedResult, normalize, parse_number

# "Wordle", the puzzle number (may contain , or . as thousands separator),
# then the guesses (1-6 or X), "/6" and an optional "*" for hard mode.
HEADER = re.compile(r"Wordle\s+([\d.,\s]*\d)\s+([1-6X])/6(\*?)", re.IGNORECASE)


class Wordle(Game):
    slug = "wordle"
    name = "Wordle"
    url = "https://www.nytimes.com/games/wordle"

    def parse(self, text):
        text = normalize(text)
        match = HEADER.search(text)
        if not match:
            return None
        number, guesses, hard = match.groups()
        solved = guesses.upper() != "X"
        grid = [line for line in text.split("\n") if re.fullmatch(r"[⬛⬜🟨🟩🟦🟧]{5}", line)]
        return ParsedResult(
            puzzle=parse_number(number),
            solved=solved,
            score=int(guesses) if solved else None,
            details={"hard_mode": bool(hard), "grid": grid},
        )

    def summary(self, result):
        guesses = result.score if result.solved else "X"
        star = "*" if result.details.get("hard_mode") else ""
        return f"{guesses}/6{star}"
