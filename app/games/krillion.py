"""krillion.io — https://krillion.io

TODO: I don't know what the krillion share text looks like yet. This parser
is a placeholder that accepts any text mentioning "krillion" and a "#<number>".
Replace it once we have real examples.
"""

import re

from .base import Game, ParsedResult, normalize, parse_number

HEADER = re.compile(r"krillion.*?#\s*([\d.,]+)", re.IGNORECASE | re.DOTALL)


class Krillion(Game):
    slug = "krillion"
    name = "krillion"
    url = "https://krillion.io"

    def parse(self, text):
        text = normalize(text)
        match = HEADER.search(text)
        if not match:
            return None
        return ParsedResult(puzzle=parse_number(match.group(1)), solved=True, score=None)

    def summary(self, result):
        return "✓"
