"""Login, logout and personal settings."""

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user

from .i18n import LANGUAGES, translate as _
from .models import User, db

bp = Blueprint("auth", __name__)

MIN_PASSWORD_LENGTH = 8


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    if request.method == "POST":
        user = User.query.filter_by(username=request.form.get("username", "").strip()).first()
        if user and user.check_password(request.form.get("password", "")):
            login_user(user, remember=True)
            return redirect(url_for("main.index"))
        flash(_("login_failed"), "error")
    return render_template("login.html")


@bp.route("/language/<code>")
def set_language(code):
    """Language switch for the login page (logged-in users use the settings)."""
    if code in LANGUAGES:
        session["language"] = code
        if current_user.is_authenticated:
            current_user.language = code
            db.session.commit()
    return redirect(request.referrer or url_for("main.index"))


@bp.route("/logout", methods=["POST"])
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":
        if request.form.get("form") == "preferences":
            if request.form.get("language") in LANGUAGES:
                current_user.language = request.form["language"]
            current_user.hide_spoilers = "hide_spoilers" in request.form
            db.session.commit()
            flash(_("settings_saved"), "success")
        elif request.form.get("form") == "password":
            new_password = request.form.get("new_password", "")
            if not current_user.check_password(request.form.get("current_password", "")):
                flash(_("password_wrong"), "error")
            elif len(new_password) < MIN_PASSWORD_LENGTH:
                flash(_("password_too_short"), "error")
            else:
                current_user.set_password(new_password)
                db.session.commit()
                flash(_("password_changed"), "success")
        return redirect(url_for("auth.settings"))
    return render_template("settings.html")
