"""Shared building blocks for all game parsers.

Every game lives in its own module (wordle.py, connections.py, ...) and
defines a subclass of `Game`. To add a new game:

1. Copy one of the existing modules, e.g. wordle.py.
2. Change `slug`, `name`, `url` and the `parse()` method.
3. Register the class in `games/__init__.py`.
"""

from dataclasses import dataclass, field


@dataclass
class ParsedResult:
    """What a parser extracts from a pasted share text."""

    puzzle: int  # puzzle number, e.g. 1621 for "Wordle 1,621 4/6"
    solved: bool  # did the player finish the puzzle?
    score: int | None  # the game's main number (guesses, mistakes, ...); lower is better
    details: dict = field(default_factory=dict)  # anything extra worth showing


class Game:
    slug = ""  # short id used in URLs and the database, e.g. "wordle"
    name = ""  # display name
    url = ""  # where the game is played
    # Lower score = better for every game so far. Set to False for a game where
    # a higher score wins.
    lower_is_better = True

    def parse(self, text: str) -> ParsedResult | None:
        """Return a ParsedResult if `text` is a share text of this game, else None."""
        raise NotImplementedError

    def summary(self, result) -> str:
        """Short text shown in tables, e.g. "4/6". `result` is a models.Result."""
        return str(result.score) if result.score is not None else "–"

    # Games with several modes that are compared separately (e.g. LoLdle) list
    # them here; each mode then gets its own table on the stats page.
    categories = [None]

    def category_title(self, category) -> str:
        """Heading of a stats table."""
        return self.name

    def stats_entry(self, result, category):
        """(solved, score) of a result in a category, or None if it wasn't played."""
        return result.solved, result.score

    def bucket(self, score: int) -> int:
        """Group scores for the distribution on the stats page (default: none)."""
        return score

    def bucket_label(self, bucket: int) -> str:
        return str(bucket)

    def spoiler_free_summary(self, result) -> str:
        """What other players see before they have played this puzzle themselves."""
        return "✓"


def normalize(text: str) -> str:
    """Clean up pasted text: unify line endings and strip whitespace."""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    return "\n".join(line.strip() for line in lines).strip()


def parse_number(raw: str) -> int:
    """Turn "1,621", "1.621" or "1 621" into 1621."""
    return int("".join(ch for ch in raw if ch.isdigit()))
