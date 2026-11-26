"""Parser tests. When you get a share text that parses wrongly, add it here."""

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
