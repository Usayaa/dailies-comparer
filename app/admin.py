"""Admin page: create, reset and delete user accounts."""

import secrets
from functools import wraps

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from .auth import MIN_PASSWORD_LENGTH
from .i18n import translate as _
from .models import User, db

bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(view):
    """Like @login_required, but the user must also be an admin."""

    @wraps(view)
    @login_required
    def wrapper(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return view(*args, **kwargs)

    return wrapper


def random_password():
    # e.g. "k3Fq-9xLp-Tz2m": easy to read out loud or send via WhatsApp
    alphabet = "abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "-".join("".join(secrets.choice(alphabet) for _ in range(4)) for _ in range(3))


@bp.route("/", methods=["GET", "POST"])
@admin_required
def users():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "") or random_password()
        if not username:
            return redirect(url_for("admin.users"))
        if User.query.filter_by(username=username).first():
            flash(_("user_exists"), "error")
        elif len(password) < MIN_PASSWORD_LENGTH:
            flash(_("password_too_short"), "error")
        else:
            user = User(username=username, is_admin="is_admin" in request.form)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash(_("user_created", name=username), "success")
            flash(_("password_reset_done", name=username, password=password), "password")
        return redirect(url_for("admin.users"))
    return render_template("admin/users.html", users=User.query.order_by(User.username).all())


@bp.route("/<int:user_id>/reset-password", methods=["POST"])
@admin_required
def reset_password(user_id):
    user = db.get_or_404(User, user_id)
    password = random_password()
    user.set_password(password)
    db.session.commit()
    flash(_("password_reset_done", name=user.username, password=password), "password")
    return redirect(url_for("admin.users"))


@bp.route("/<int:user_id>/delete", methods=["POST"])
@admin_required
def delete_user(user_id):
    user = db.get_or_404(User, user_id)
    if user.id == current_user.id:
        flash(_("cannot_delete_self"), "error")
    else:
        db.session.delete(user)  # also deletes their results (cascade)
        db.session.commit()
        flash(_("user_deleted", name=user.username), "success")
    return redirect(url_for("admin.users"))
