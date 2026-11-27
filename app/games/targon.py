"""Targon Climb — https://targonclimb.com

Example share text:

    Targon Climb #16 · 1,500 m
    🧗 Reached Lunari Hollow

    Higher than 32% of players today
    https://targonclimb.com

Score = metres climbed (higher is better).
"""

import re

from .base import Game, ParsedResult, normalize, parse_number

# Puzzle number, anything in between (" · "), then the metres.
HEADER = re.compile(r"Targon Climb\s*#\s*(\d[\d.,]*)\D+?(\d[\d.,]*)\s*m\b", re.IGNORECASE)
REACHED = re.compile(r"Reached\s+(.+)", re.IGNORECASE)
PERCENT = re.compile(r"Higher than\s+(\d+)\s*%", re.IGNORECASE)


class TargonClimb(Game):
    slug = "targon"
    name = "Targon Climb"
    url = "https://targonclimb.com"
    lower_is_better = False  # more metres is better

    def parse(self, text):
        text = normalize(text)
        match = HEADER.search(text)
        if not match:
            return None
        reached = REACHED.search(text)
        percent = PERCENT.search(text)
        return ParsedResult(
            puzzle=parse_number(match.group(1)),
            solved=True,
            score=parse_number(match.group(2)),
            details={
                "reached": reached.group(1).strip() if reached else None,
                "higher_than_percent": int(percent.group(1)) if percent else None,
            },
        )

    def summary(self, result):
        return f"{result.score} m"

    def bucket(self, score):
        return score // 500 * 500  # distribution in steps of 500 m

    def bucket_label(self, bucket):
        return f"{bucket}+"
