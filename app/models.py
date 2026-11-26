"""Database tables.

There are only two:
- User:   one row per friend (created by the admin, no public sign-up).
- Result: one row per pasted score (user + game + puzzle number).
"""

from datetime import datetime, timezone

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

from .games import GAMES

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    language = db.Column(db.String(2), default="de", nullable=False)
    # No-spoiler mode: hide other players' results for a puzzle until you have
    # submitted your own. On by default, each user can switch it off.
    hide_spoilers = db.Column(db.Boolean, default=True, nullable=False)

    results = db.relationship("Result", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password):
        # Never store the password itself, only a salted hash of it.
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    game_slug = db.Column(db.String(30), nullable=False)
    puzzle = db.Column(db.Integer, nullable=False)
    solved = db.Column(db.Boolean, nullable=False)
    score = db.Column(db.Integer)  # meaning depends on the game, see games/*.py
    details = db.Column(db.JSON, default=dict, nullable=False)
    # The original pasted text. Kept so results can be re-parsed when a parser
    # is improved later (see the `flask reparse` command).
    raw_text = db.Column(db.Text, nullable=False)
    submitted_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    user = db.relationship("User", back_populates="results")

    # Each player can submit each puzzle only once.
    __table_args__ = (db.UniqueConstraint("user_id", "game_slug", "puzzle"),)

    @property
    def game(self):
        return GAMES[self.game_slug]

    @property
    def summary(self):
        return self.game.summary(self)
