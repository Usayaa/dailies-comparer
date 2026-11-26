"""Registry of all supported games.

`GAMES` maps a slug ("wordle") to a game instance. The order here is the order
games appear on the website.
"""

from .connections import Connections
from .krillion import Krillion
from .strands import Strands
from .travle import Travle
from .wordle import Wordle

GAMES = {game.slug: game for game in [Wordle(), Connections(), Strands(), Travle(), Krillion()]}


def detect(text):
    """Find out which game a pasted text belongs to.

    Returns (game, parsed_result), or (None, None) if no parser recognises it.
    """
    for game in GAMES.values():
        parsed = game.parse(text)
        if parsed is not None:
            return game, parsed
    return None, None
