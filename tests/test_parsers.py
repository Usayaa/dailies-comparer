"""Parser tests. When you get a share text that parses wrongly, add it here.

The REAL_* texts are copied from the actual games.
"""

from app.games import detect


def test_wordle_solved():
    game, r = detect("Wordle 1,621 4/6\n\n⬛🟨⬛⬛⬛\n🟩🟩⬛🟨⬛\n🟩🟩🟩🟨⬛\n🟩🟩🟩🟩🟩")
    assert game.slug == "wordle"
    assert (r.puzzle, r.solved, r.score) == (1621, True, 4)
    assert len(r.details["grid"]) == 4
    assert r.details["hard_mode"] is False


def test_wordle_failed_hard_mode_german_separator():
    game, r = detect("Wordle 1.621 X/6*\n\n⬛⬛⬛⬛⬛")
    assert (r.puzzle, r.solved, r.score, r.details["hard_mode"]) == (1621, False, None, True)


def test_connections():
    text = "Connections\nPuzzle #512\n🟨🟨🟨🟨\n🟩🟦🟩🟩\n🟩🟩🟩🟩\n🟦🟦🟦🟦\n🟪🟪🟪🟪"
    game, r = detect(text)
    assert game.slug == "connections"
    assert (r.puzzle, r.solved, r.score) == (512, True, 1)
    assert r.details["order"] == ["yellow", "green", "blue", "purple"]


def test_connections_lost():
    text = "Connections\nPuzzle #513\n🟨🟩🟨🟨\n🟨🟨🟨🟨\n🟩🟦🟩🟩\n🟦🟪🟦🟦\n🟪🟩🟪🟪"
    _, r = detect(text)
    assert (r.solved, r.score) == (False, 4)


def test_strands():
    game, r = detect("Strands #245\n“Make a splash”\n🔵🔵💡🔵\n🟡🔵🔵")
    assert game.slug == "strands"
    assert (r.puzzle, r.score) == (245, 1)
    assert r.details["theme"] == "Make a splash"
    assert r.details["spangram_at"] == 4


def test_travle():
    game, r = detect("#travle #612 +2 (1 hint)\n🟢🟢🟧✅\nhttps://travle.earth")
    assert game.slug == "travle"
    assert (r.puzzle, r.score, r.details["hints"]) == (612, 2, 1)


def test_windows_line_endings_and_whitespace():
    _, r = detect("  Wordle 1,000 3/6 \r\n\r\n🟩🟩🟩🟩🟩\r\n")
    assert (r.puzzle, r.score) == (1000, 3)


def test_unknown_text():
    assert detect("hello there") == (None, None)


def test_krillion():
    game, r = detect("Krillion #134 🦐\n330\n\n🏮🐟🦑🐟🫧🏮🐟")
    assert game.slug == "krillion"
    assert (r.puzzle, r.solved, r.score) == (134, True, 330)
    assert r.details["answers"] == "🏮🐟🦑🐟🫧🏮🐟"


def test_real_wordle():
    _, r = detect("Wordle 1,986 5/6\n\n⬛⬛⬛🟨🟩\n🟨🟨⬛⬛🟩\n⬛🟩🟩🟩🟩\n⬛🟩🟩🟩🟩\n🟩🟩🟩🟩🟩")
    assert (r.puzzle, r.solved, r.score, len(r.details["grid"])) == (1986, True, 5, 5)


def test_real_connections_failed():
    text = "Connections\nPuzzle #1264\n🟩🟩🟩🟩\n🟦🟪🟦🟦\n🟪🟨🟦🟦\n🟦🟪🟦🟨\n🟦🟪🟦🟪"
    _, r = detect(text)
    assert (r.puzzle, r.solved, r.score, r.details["order"]) == (1264, False, 4, ["green"])


def test_real_strands():
    _, r = detect("Strands #998\n“A crowded table”\n💡🔵💡🔵\n💡🔵💡🔵\n🟡🔵")
    assert (r.puzzle, r.score, r.details["theme"], r.details["spangram_at"]) == (998, 4, "A crowded table", 5)


def test_real_travle():
    _, r = detect("#travle #1443 +1\n✅✅✅🟩✅✅✅🟧✅\nhttps://travle.earth")
    assert (r.puzzle, r.solved, r.score) == (1443, True, 1)
    assert r.details["grid"] == "✅✅✅🟩✅✅✅🟧✅"


def test_real_travle_perfect():
    _, r = detect("#travle #859 +0 (Perfect)\n✅✅✅✅✅✅✅\nhttps://travle.earth")
    assert (r.puzzle, r.solved, r.score, r.details["hints"]) == (859, True, 0, 0)


def test_real_travle_failed():
    _, r = detect("#travle #38 (2 away)\n🟥🟥🟥🟥🟩🟥🟥\nhttps://travle.earth")
    assert (r.puzzle, r.solved, r.score, r.details["away"]) == (38, False, None, 2)
    assert r.details["grid"] == "🟥🟥🟥🟥🟩🟥🟥"


def test_travle_regional_variant_is_ignored():
    assert detect("#travle_usa #50 +1\n✅✅") == (None, None)


def test_real_wordle_de_is_not_english_wordle():
    game, r = detect("Wordle auf Deutsch 362 1/6\n\n🟩🟩🟩🟩🟩\n\nsz.de/wordle")
    assert game.slug == "wordle-de"
    assert (r.puzzle, r.solved, r.score, r.details["grid"]) == (362, True, 1, ["🟩🟩🟩🟩🟩"])


def test_real_targon():
    text = (
        "Targon Climb #16 · 1,500 m\n🧗 Reached Lunari Hollow\n\n"
        "Higher than 32% of players today\nhttps://targonclimb.com"
    )
    game, r = detect(text)
    assert game.slug == "targon"
    assert (r.puzzle, r.solved, r.score) == (16, True, 1500)
    assert r.details == {"reached": "Lunari Hollow", "higher_than_percent": 32}


def test_real_loldle():
    text = (
        "I've completed all the modes of #LoLdle #1604 today:\n❓ Classic: 7\n💬 Quote: 1\n"
        "🔥 Ability: 3 🧠 ✓\n😀 Emoji: 2\n🎨 Splash: 2 ✓\n\nhttps://loldle.net"
    )
    game, r = detect(text)
    assert game.slug == "loldle"
    assert r.puzzle == 1604
    modes = r.details["modes"]
    assert {k: v["guesses"] for k, v in modes.items()} == {
        "classic": 7, "quote": 1, "ability": 3, "emoji": 2, "splash": 2,
    }
    assert modes["ability"] == {"guesses": 3, "bonus": True, "brain": True}
    assert modes["classic"]["bonus"] is False


def test_loldle_partial_modes():
    _, r = detect("#LoLdle #1605\n❓ Classic: 4\n💬 Quote: 2")
    assert set(r.details["modes"]) == {"classic", "quote"}


def test_real_wordle_de_failed():
    text = (
        "Wordle auf Deutsch 362 X/6\n\n⬜⬜⬜⬜⬜\n⬜⬜⬜⬜⬜\n⬜⬜⬜⬜⬜\n"
        "⬜⬜⬜⬜⬜\n⬜⬜⬜⬜⬜\n⬜⬜⬜⬜🟨\n\nsz.de/wordle"
    )
    game, r = detect(text)
    assert game.slug == "wordle-de"
    assert (r.puzzle, r.solved, r.score) == (362, False, None)
    assert len(r.details["grid"]) == 6  # light-mode ⬜ squares are kept too


def test_real_connections_failed_without_and_with_one_group():
    from types import SimpleNamespace

    from app.games import GAMES

    none = "Connections\nPuzzle #1266\n🟩🟦🟩🟩\n🟩🟩🟪🟩\n🟩🟦🟩🟪\n🟩🟦🟪🟩"
    one = "Connections\nPuzzle #1266\n🟩🟦🟩🟩\n🟩🟦🟩🟩\n🟩🟩🟪🟩\n🟩🟩🟩🟩\n🟨🟦🟨🟦"
    summaries = []
    for text in (none, one):
        game, r = detect(text)
        assert (game.slug, r.puzzle, r.solved, r.score) == ("connections", 1266, False, 4)
        summaries.append(GAMES["connections"].summary(SimpleNamespace(**vars(r))))
    assert summaries == ["0/4", "1/4"]


def test_connections_summary_solved():
    from types import SimpleNamespace

    from app.games import GAMES

    _, r = detect("Connections\nPuzzle #512\n🟨🟨🟨🟨\n🟩🟦🟩🟩\n🟩🟩🟩🟩\n🟦🟦🟦🟦\n🟪🟪🟪🟪")
    assert GAMES["connections"].summary(SimpleNamespace(**vars(r))) == "4/4 · 1✗"
