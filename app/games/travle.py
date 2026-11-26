"""Travle — https://travle.earth

Example share texts (the normal daily route puzzle):

    #travle #1443 +1
    ✅✅✅🟩✅✅✅🟧✅
    https://travle.earth

    #travle #859 +0 (Perfect)
    ✅✅✅✅✅✅✅
    https://travle.earth

    #travle #38 (2 away)          <- failed: 2 countries away from a complete route
    🟥🟥🟥🟥🟩🟥🟥
    https://travle.earth

"+1" means one guess more than the shortest possible route.
Score = that number of extra guesses (lower is better). A failed game has no
score; how far away it ended is stored in details["away"]. The emoji row shows
how close each guessed country was to the route.
"""

import re

from ..i18n import translate
from .base import Game, ParsedResult, normalize, parse_number

# Only the plain "#travle", not regional variants like "#travle_usa".
HEADER = re.compile(r"#travle\s+#\s*([\d.,]+)(?:\s+\+(\d+))?", re.IGNORECASE)
HINTS = re.compile(r"\((\d+)\s+hints?\)", re.IGNORECASE)
AWAY = re.compile(r"\((\d+)\s+away\)", re.IGNORECASE)


class Travle(Game):
    slug = "travle"
    name = "Travle"
    url = "https://travle.earth"

    def parse(self, text):
        text = normalize(text)
        match = HEADER.search(text)
        if not match:
            return None
        number, extra = match.groups()
        hints = HINTS.search(text)
        away = AWAY.search(text)
        # The emoji row is the line right after the header.
        lines = [line for line in text.split("\n") if line]
        header_index = next(i for i, line in enumerate(lines) if HEADER.search(line))
        grid = lines[header_index + 1] if header_index + 1 < len(lines) else ""
        if grid.startswith("http"):
            grid = ""
        return ParsedResult(
            puzzle=parse_number(number),
            solved=extra is not None,
            score=int(extra) if extra is not None else None,
            details={
                "hints": int(hints.group(1)) if hints else 0,
                "away": int(away.group(1)) if away else None,
                "grid": grid,
            },
        )

    def summary(self, result):
        if not result.solved:
            away = result.details.get("away")
            return translate("travle_away", n=away) if away else "✗"
        text = f"+{result.score}"
        if result.details.get("hints"):
            text += f" ({result.details['hints']} 💡)"
        return text
