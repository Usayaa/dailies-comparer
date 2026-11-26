"""Travle — https://travle.earth

Example share text:

    #travle #612 +2 (1 hint)
    🟢🟢🟧✅
    https://travle.earth

"+2" means two guesses more than the shortest possible route.
Score = that number of extra guesses (lower is better).

TODO: verify against real share texts — in particular what a failed game and
the regional variants (e.g. "#travle_usa") look like.
"""

import re

from .base import Game, ParsedResult, normalize, parse_number

HEADER = re.compile(r"#travle\s+#\s*([\d.,]+)\s+\+(\d+)", re.IGNORECASE)
HINTS = re.compile(r"\((\d+)\s+hints?\)", re.IGNORECASE)


class Travle(Game):
    slug = "travle"
    name = "Travle"
    url = "https://travle.earth"

    def parse(self, text):
        text = normalize(text)
        match = HEADER.search(text)
        if not match:
            return None
        hints = HINTS.search(text)
        return ParsedResult(
            puzzle=parse_number(match.group(1)),
            solved=True,
            score=int(match.group(2)),
            details={
                "hints": int(hints.group(1)) if hints else 0,
                "grid": "".join(re.findall(r"[🟢🟡🟠🟧🔴🟥✅⬛⬜]", text)),
            },
        )

    def summary(self, result):
        text = f"+{result.score}"
        if result.details.get("hints"):
            text += f" ({result.details['hints']} 💡)"
        return text
