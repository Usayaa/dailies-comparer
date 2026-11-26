"""The main pages: overview, submitting results, game history, puzzle details, stats."""

from collections import Counter

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError

from .games import GAMES, detect
from .i18n import translate as _
from .models import Result, User, db

bp = Blueprint("main", __name__)

PUZZLES_PER_PAGE = 20
PUZZLES_ON_DASHBOARD = 3


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def all_users():
    return User.query.order_by(User.username).all()


def my_puzzles(game_slug):
    """Set of puzzle numbers the logged-in user has submitted for a game."""
    rows = db.session.query(Result.puzzle).filter_by(user_id=current_user.id, game_slug=game_slug)
    return {puzzle for (puzzle,) in rows}


def may_see(result, played):
    """No-spoiler rule: may the current user see the details of `result`?

    `played` is the set of puzzle numbers the current user has submitted.
    """
    return (
        result.user_id == current_user.id
        or not current_user.hide_spoilers
        or result.puzzle in played
    )


def build_matrix(game, puzzle_numbers):
    """Results for the given puzzles, as {puzzle: {user_id: Result}}."""
    results = Result.query.filter(
        Result.game_slug == game.slug, Result.puzzle.in_(puzzle_numbers)
    ).all()
    matrix = {puzzle: {} for puzzle in puzzle_numbers}
    for result in results:
        matrix[result.puzzle][result.user_id] = result
    return matrix


def latest_puzzles(game, limit, offset=0):
    """The newest puzzle numbers anybody has submitted for a game."""
    rows = (
        db.session.query(Result.puzzle)
        .filter_by(game_slug=game.slug)
        .distinct()
        .order_by(Result.puzzle.desc())
        .limit(limit)
        .offset(offset)
    )
    return [puzzle for (puzzle,) in rows]


def get_game(slug):
    game = GAMES.get(slug)
    if game is None:
        abort(404)
    return game


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------


@bp.route("/")
@login_required
def index():
    """Overview: the latest few puzzles of every game, everyone side by side."""
    sections = []
    for game in GAMES.values():
        puzzles = latest_puzzles(game, PUZZLES_ON_DASHBOARD)
        sections.append(
            {"game": game, "matrix": build_matrix(game, puzzles), "played": my_puzzles(game.slug)}
        )
    return render_template("index.html", sections=sections, users=all_users(), may_see=may_see)


@bp.route("/submit", methods=["GET", "POST"])
@login_required
def submit():
    text = ""
    if request.method == "POST":
        text = request.form.get("text", "")
        game, parsed = detect(text)
        if game is None:
            flash(_("unknown_game"), "error")
        else:
            result = Result(
                user_id=current_user.id,
                game_slug=game.slug,
                puzzle=parsed.puzzle,
                solved=parsed.solved,
                score=parsed.score,
                details=parsed.details,
                raw_text=text.strip(),
            )
            db.session.add(result)
            try:
                db.session.commit()
            except IntegrityError:  # the unique constraint: already submitted
                db.session.rollback()
                flash(_("already_submitted", game=game.name, puzzle=parsed.puzzle), "error")
            else:
                flash(
                    _("saved", game=game.name, puzzle=parsed.puzzle, summary=result.summary),
                    "success",
                )
                return redirect(url_for("main.puzzle", slug=game.slug, puzzle=parsed.puzzle))
    return render_template("submit.html", text=text)


@bp.route("/game/<slug>")
@login_required
def game(slug):
    """All puzzles of one game, newest first, PUZZLES_PER_PAGE at a time."""
    game = get_game(slug)
    page = max(request.args.get("page", 1, type=int), 1)
    puzzles = latest_puzzles(game, PUZZLES_PER_PAGE + 1, (page - 1) * PUZZLES_PER_PAGE)
    has_more = len(puzzles) > PUZZLES_PER_PAGE  # we fetched one extra to find out
    puzzles = puzzles[:PUZZLES_PER_PAGE]
    return render_template(
        "game.html",
        game=game,
        matrix=build_matrix(game, puzzles),
        played=my_puzzles(slug),
        users=all_users(),
        may_see=may_see,
        page=page,
        has_more=has_more,
    )


@bp.route("/game/<slug>/<int:puzzle>")
@login_required
def puzzle(slug, puzzle):
    """One puzzle: everybody's full share text."""
    game = get_game(slug)
    results = (
        Result.query.filter_by(game_slug=slug, puzzle=puzzle).order_by(Result.submitted_at).all()
    )
    return render_template(
        "puzzle.html",
        game=game,
        puzzle=puzzle,
        results=results,
        played=my_puzzles(slug),
        may_see=may_see,
    )


@bp.route("/result/<int:result_id>/delete", methods=["POST"])
@login_required
def delete_result(result_id):
    """Delete your own result, e.g. after pasting the wrong text."""
    result = db.get_or_404(Result, result_id)
    if result.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    slug, puzzle = result.game_slug, result.puzzle
    db.session.delete(result)
    db.session.commit()
    flash(_("deleted"), "success")
    return redirect(url_for("main.puzzle", slug=slug, puzzle=puzzle))


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------


def streaks(solved_puzzles, latest_puzzle):
    """(current streak, best streak) over consecutive solved puzzle numbers.

    The current streak only counts if it reaches the newest puzzle (or the one
    before, so it doesn't drop to 0 in the morning before you've played).
    """
    best = current = 0
    run = 0
    previous = None
    for number in sorted(solved_puzzles):
        run = run + 1 if previous is not None and number == previous + 1 else 1
        best = max(best, run)
        previous = number
    if previous is not None and latest_puzzle is not None and previous >= latest_puzzle - 1:
        current = run
    return current, best


def game_stats(game, results, latest_puzzle):
    """Numbers for one player and one game."""
    solved = [r for r in results if r.solved]
    scores = [r.score for r in solved if r.score is not None]
    pick_best = min if game.lower_is_better else max
    current, best_streak = streaks({r.puzzle for r in solved}, latest_puzzle)
    # Distribution: how often each score occurred; unsolved games count as "✗".
    counts = Counter(game.bucket(r.score) for r in solved if r.score is not None)
    # Best scores first: ascending, or descending for games where higher wins.
    buckets = sorted(counts, reverse=not game.lower_is_better)
    distribution = [(game.bucket_label(b), counts[b]) for b in buckets]
    failed = len(results) - len(solved)
    if failed:
        distribution.append(("✗", failed))
        counts["✗"] = failed
    return {
        "played": len(results),
        "solved": len(solved),
        "solve_rate": round(100 * len(solved) / len(results)) if results else 0,
        "average": round(sum(scores) / len(scores), 2) if scores else None,
        "best": pick_best(scores) if scores else None,
        "streak": current,
        "best_streak": best_streak,
        "distribution": distribution,
        "max_count": max(counts.values()) if counts else 0,
    }


@bp.route("/stats")
@login_required
def stats():
    """Per game, every player's numbers side by side."""
    users = all_users()
    tables = []
    for game in GAMES.values():
        results = Result.query.filter_by(game_slug=game.slug).all()
        latest = max((r.puzzle for r in results), default=None)
        per_user = {
            user.id: game_stats(game, [r for r in results if r.user_id == user.id], latest)
            for user in users
        }
        tables.append({"game": game, "per_user": per_user})
    return render_template("stats.html", tables=tables, users=users)
