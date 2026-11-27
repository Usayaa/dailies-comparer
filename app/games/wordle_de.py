"""Wordle auf Deutsch (Süddeutsche Zeitung) — https://sz.de/wordle

Example share text:

    Wordle auf Deutsch 362 1/6

    🟩🟩🟩🟩🟩

    sz.de/wordle

Exactly the same game as Wordle, only the first line differs, so this class
reuses everything from wordle.py and just swaps the header pattern.
"""

import re

from .wordle import Wordle

HEADER = re.compile(r"Wordle auf Deutsch\s+([\d.,\s]*\d)\s+([1-6X])/6(\*?)", re.IGNORECASE)


class WordleDe(Wordle):
    slug = "wordle-de"
    name = "Wordle DE"
    url = "https://sz.de/wordle"
    header = HEADER
