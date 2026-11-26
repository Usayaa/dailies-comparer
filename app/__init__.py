"""Application setup ("app factory").

Run locally with:   flask --app app run --debug
Production:         gunicorn "app:create_app()"   (see README.md)
"""

import os
import secrets
from datetime import UTC
from zoneinfo import ZoneInfo

import click
from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix

from .games import GAMES
from .i18n import LANGUAGES, get_language, translate
from .models import Result, User, db

login_manager = LoginManager()
csrf = CSRFProtect()  # protects every POST form against cross-site request forgery


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    os.makedirs(app.instance_path, exist_ok=True)

    app.config.update(
        # The secret key signs the login cookie. Set it in production via the
        # environment (see deploy/dailies.env.example), otherwise everyone gets
        # logged out on every restart.
        SECRET_KEY=os.environ.get("SECRET_KEY") or secrets.token_hex(32),
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            "DATABASE_URL", "sqlite:///" + os.path.join(app.instance_path, "dailies.sqlite")
        ),
        TIMEZONE=os.environ.get("TIMEZONE", "Europe/Berlin"),
        SESSION_COOKIE_SECURE=os.environ.get("SESSION_COOKIE_SECURE", "0") == "1",
        SESSION_COOKIE_SAMESITE="Lax",
        REMEMBER_COOKIE_DURATION=60 * 60 * 24 * 365,  # stay logged in for a year
    )
    if test_config:
        app.config.update(test_config)

    # Behind Nginx/Caddy: trust the X-Forwarded-* headers from one proxy so
    # Flask knows the original scheme (https) and client IP.
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = None

    from . import admin, auth, main

    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(admin.bp)

    local_zone = ZoneInfo(app.config["TIMEZONE"])

    @app.template_filter("localtime")
    def localtime(value):
        """Show a stored UTC timestamp in our local time zone."""
        return value.replace(tzinfo=UTC).astimezone(local_zone).strftime("%d.%m.%Y %H:%M")

    @app.context_processor
    def template_helpers():
        # These names are available in every template.
        return {"_": translate, "GAMES": GAMES, "LANGUAGES": LANGUAGES, "lang": get_language()}

    with app.app_context():
        db.create_all()  # creates the tables on first start; does nothing later

    register_commands(app)
    return app


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def register_commands(app):
    """Command-line helpers, e.g. `flask --app app create-user lukas --admin`."""

    @app.cli.command("create-user")
    @click.argument("username")
    @click.option("--admin", is_flag=True, help="Give the user access to the admin page.")
    @click.password_option()
    def create_user(username, admin, password):
        """Create a user account."""
        if User.query.filter_by(username=username).first():
            raise click.ClickException(f"User {username!r} already exists.")
        user = User(username=username, is_admin=admin)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        click.echo(f"Created user {username!r}{' (admin)' if admin else ''}.")

    @app.cli.command("reparse")
    def reparse():
        """Re-run the parsers on all stored share texts (after improving a parser)."""
        changed = 0
        for result in Result.query.all():
            parsed = result.game.parse(result.raw_text)
            if parsed is None:
                click.echo(f"Could not parse result {result.id} any more, leaving it as is.")
                continue
            new = (parsed.puzzle, parsed.solved, parsed.score, parsed.details)
            if new != (result.puzzle, result.solved, result.score, result.details):
                result.puzzle, result.solved, result.score, result.details = new
                changed += 1
        db.session.commit()
        click.echo(f"Updated {changed} result(s).")
