"""Registry of all supported games.

`GAMES` maps a slug ("wordle") to a game instance. The order here is the order
games appear on the website.
"""

from .connections import Connections
from .krillion import Krillion
from .loldle import Loldle
from .strands import Strands
from .targon import TargonClimb
from .travle import Travle
from .wordle import Wordle
from .wordle_de import WordleDe

GAMES = {
    game.slug: game
    for game in [
        Wordle(),
        WordleDe(),
        Connections(),
        Strands(),
        Travle(),
        Krillion(),
        TargonClimb(),
        Loldle(),
    ]
}


def detect(text):
    """Find out which game a pasted text belongs to.

    Returns (game, parsed_result), or (None, None) if no parser recognises it.
    """
    for game in GAMES.values():
        parsed = game.parse(text)
        if parsed is not None:
            return game, parsed
    return None, None
