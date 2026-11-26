"""End-to-end tests of the web pages using Flask's test client."""

import pytest

from app import create_app
from app.models import User, db

WORDLE = "Wordle 1,621 4/6\n\n⬛🟨⬛⬛⬛\n🟩🟩🟩🟩🟩"


@pytest.fixture
def app(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "WTF_CSRF_ENABLED": False,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'test.sqlite'}",
        }
    )
    with app.app_context():
        db.create_all()
        for name, admin in [("anna", True), ("ben", False)]:
            user = User(username=name, is_admin=admin, language="en")
            user.set_password("password123")
            db.session.add(user)
        db.session.commit()
    return app


def client_for(app, username):
    client = app.test_client()
    client.post("/login", data={"username": username, "password": "password123"})
    return client


def test_login_required(app):
    response = app.test_client().get("/")
    assert response.status_code == 302 and "/login" in response.location


def test_wrong_password(app):
    response = app.test_client().post(
        "/login", data={"username": "anna", "password": "nope"}, follow_redirects=True
    )
    assert "Benutzername oder Passwort falsch".encode() in response.data  # German by default


def test_submit_and_duplicate(app):
    anna = client_for(app, "anna")
    response = anna.post("/submit", data={"text": WORDLE}, follow_redirects=True)
    assert b"Saved Wordle #1621: 4/6" in response.data
    response = anna.post("/submit", data={"text": WORDLE}, follow_redirects=True)
    assert b"already submitted" in response.data


def test_unknown_text(app):
    response = client_for(app, "anna").post("/submit", data={"text": "hi"})
    assert b"couldn&#39;t match" in response.data


def test_no_spoilers_until_played(app):
    client_for(app, "anna").post("/submit", data={"text": WORDLE})
    ben = client_for(app, "ben")
    page = ben.get("/game/wordle/1621").data
    assert b"4/6" not in page and b"Play this puzzle first" in page
    # Ben plays it too, now he can see Anna's result.
    ben.post("/submit", data={"text": "Wordle 1,621 X/6\n\n⬛⬛⬛⬛⬛"})
    assert b"4/6" in ben.get("/game/wordle/1621").data


def test_spoiler_toggle_off(app):
    client_for(app, "anna").post("/submit", data={"text": WORDLE})
    ben = client_for(app, "ben")
    ben.post("/settings", data={"form": "preferences", "language": "en"})  # checkbox unticked
    assert b"4/6" in ben.get("/").data


def test_admin_only(app):
    assert client_for(app, "ben").get("/admin/").status_code == 403
    anna = client_for(app, "anna")
    response = anna.post("/admin/", data={"username": "carla"}, follow_redirects=True)
    assert b"User carla created" in response.data


def test_cannot_delete_others_result(app):
    client_for(app, "ben").post("/submit", data={"text": WORDLE})
    with app.app_context():
        from app.models import Result

        result_id = Result.query.one().id
    # anna is admin, so create a non-admin third user to try it
    anna = client_for(app, "anna")
    anna.post("/admin/", data={"username": "carla", "password": "password123"})
    carla = client_for(app, "carla")
    assert carla.post(f"/result/{result_id}/delete").status_code == 403


def test_stats_page(app):
    anna = client_for(app, "anna")
    anna.post("/submit", data={"text": WORDLE})
    anna.post("/submit", data={"text": "Wordle 1,622 3/6\n\n🟩🟩🟩🟩🟩"})
    page = anna.get("/stats").data
    assert b"3.5" in page  # average


def test_german_is_default(app):
    with app.app_context():
        user = User(username="dora", language="de")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()
    assert b"Statistiken" in client_for(app, "dora").get("/").data
