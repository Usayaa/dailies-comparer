"""LoLdle — https://loldle.net

Example share text:

    I've completed all the modes of #LoLdle #1604 today:
    ❓ Classic: 7
    💬 Quote: 1
    🔥 Ability: 3 🧠 ✓
    😀 Emoji: 2
    🎨 Splash: 2 ✓

    https://loldle.net

LoLdle has several modes that are compared separately, so instead of a single
score this stores the guesses per mode in details["modes"], e.g.
{"classic": {"guesses": 7, "bonus": False}, ...}. "✓" (the bonus question was
answered correctly) and "🧠" are kept but not scored.

Lower guesses are better. LoLdle can't be failed. Modes missing from a share
text (if you didn't play them) are simply not stored.
"""

import re

from .base import Game, ParsedResult, normalize, parse_number

HEADER = re.compile(r"#LoLdle\s*#\s*(\d[\d.,]*)", re.IGNORECASE)
# One line per mode, e.g. "🔥 Ability: 3 🧠 ✓"
MODE_LINE = re.compile(r"(Classic|Quote|Ability|Emoji|Splash)\s*:\s*(\d+)(.*)", re.IGNORECASE)

# mode key -> (icon, name) in the order LoLdle shows them
MODES = {
    "classic": ("❓", "Classic"),
    "quote": ("💬", "Quote"),
    "ability": ("🔥", "Ability"),
    "emoji": ("😀", "Emoji"),
    "splash": ("🎨", "Splash"),
}


class Loldle(Game):
    slug = "loldle"
    name = "LoLdle"
    url = "https://loldle.net"
    categories = list(MODES)  # one stats table per mode

    def parse(self, text):
        text = normalize(text)
        match = HEADER.search(text)
        if not match:
            return None
        modes = {}
        for mode, guesses, rest in MODE_LINE.findall(text):
            modes[mode.lower()] = {
                "guesses": int(guesses),
                "bonus": "✓" in rest,
                "brain": "🧠" in rest,
            }
        if not modes:
            return None
        return ParsedResult(
            puzzle=parse_number(match.group(1)),
            solved=True,
            score=sum(m["guesses"] for m in modes.values()),  # total, not shown
            details={"modes": modes},
        )

    def summary(self, result):
        # One mode per line keeps the table column narrow on phones
        # (result tables keep line breaks, see style.css).
        modes = result.details.get("modes", {})
        return "\n".join(
            f"{icon}{modes[key]['guesses']}" for key, (icon, _) in MODES.items() if key in modes
        )

    def category_title(self, category):
        icon, name = MODES[category]
        return f"LoLdle {icon} {name}"

    def stats_entry(self, result, category):
        mode = result.details.get("modes", {}).get(category)
        return (True, mode["guesses"]) if mode else None
