"""Strands (NYT) — https://www.nytimes.com/games/strands

Example share text:

    Strands #245
    “Make a splash”
    🔵🔵💡🔵
    🟡🔵🔵

🔵 = theme word found, 🟡 = spangram, 💡 = hint used.
The theme line ("Make a splash") is a spoiler, so it is only shown to players
who have played the puzzle themselves.
Score = number of hints (lower is better). Strands cannot be failed.
"""

import re

from .base import Game, ParsedResult, normalize, parse_number

HEADER = re.compile(r"Strands\s*#\s*([\d.,]+)", re.IGNORECASE)
# The theme is quoted with “curly” or "straight" quotes on its own line.
THEME = re.compile(r"^[“\"](.+)[”\"]$", re.MULTILINE)
EMOJI = re.compile(r"[🔵🟡💡]")


class Strands(Game):
    slug = "strands"
    name = "Strands"
    url = "https://www.nytimes.com/games/strands"

    def parse(self, text):
        text = normalize(text)
        match = HEADER.search(text)
        if not match:
            return None
        theme = THEME.search(text)
        sequence = "".join(EMOJI.findall(text))
        hints = sequence.count("💡")
        # 1-based position of the spangram among the words found (not hints).
        words = sequence.replace("💡", "")
        spangram_at = words.index("🟡") + 1 if "🟡" in words else None
        return ParsedResult(
            puzzle=parse_number(match.group(1)),
            solved=True,
            score=hints,
            details={
                "theme": theme.group(1) if theme else None,
                "sequence": sequence,
                "spangram_at": spangram_at,
            },
        )

    def summary(self, result):
        if result.score == 0:
            return "0 💡"
        return f"{result.score} 💡"
