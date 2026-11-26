"""Travle — https://travle.earth

Example share text (the normal daily route puzzle):

    #travle #1443 +1
    ✅✅✅🟩✅✅✅🟧✅
    https://travle.earth

"+1" means one guess more than the shortest possible route.
Score = that number of extra guesses (lower is better). The emoji row shows
how close each guessed country was to the route.

TODO: we haven't seen the share text of a failed game yet. For now, a text
with "#travle #<number>" but without "+N" is saved as not solved; once we
know the real format, fix it here and run `flask --app app reparse`.
"""

import re

from .base import Game, ParsedResult, normalize, parse_number

# Only the plain "#travle", not regional variants like "#travle_usa".
HEADER = re.compile(r"#travle\s+#\s*([\d.,]+)(?:\s+\+(\d+))?", re.IGNORECASE)
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
        number, extra = match.groups()
        hints = HINTS.search(text)
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
            details={"hints": int(hints.group(1)) if hints else 0, "grid": grid},
        )

    def summary(self, result):
        if not result.solved:
            return "✗"
        text = f"+{result.score}"
        if result.details.get("hints"):
            text += f" ({result.details['hints']} 💡)"
        return text
