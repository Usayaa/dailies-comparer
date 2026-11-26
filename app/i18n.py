"""Very small German/English translation helper.

In templates use `{{ _("key") }}`. Strings may contain {placeholders}:
`{{ _("welcome", name=current_user.username) }}`.

To add a text: add a key with both languages below. To add a language: add
another entry to each dict and to LANGUAGES.
"""

from flask import session
from flask_login import current_user

LANGUAGES = {"de": "Deutsch", "en": "English"}
DEFAULT_LANGUAGE = "de"

TEXTS = {
    # Navigation
    "nav_today": {"de": "Heute", "en": "Today"},
    "nav_submit": {"de": "Ergebnis eintragen", "en": "Submit result"},
    "nav_stats": {"de": "Statistiken", "en": "Stats"},
    "nav_settings": {"de": "Einstellungen", "en": "Settings"},
    "nav_admin": {"de": "Verwaltung", "en": "Admin"},
    "nav_logout": {"de": "Abmelden", "en": "Log out"},
    # Login
    "login": {"de": "Anmelden", "en": "Log in"},
    "username": {"de": "Benutzername", "en": "Username"},
    "password": {"de": "Passwort", "en": "Password"},
    "login_failed": {"de": "Benutzername oder Passwort falsch.", "en": "Wrong username or password."},
    "please_log_in": {"de": "Bitte melde dich an.", "en": "Please log in."},
    # Dashboard
    "today_title": {"de": "Aktuelle Rätsel", "en": "Current puzzles"},
    "puzzle": {"de": "Rätsel", "en": "Puzzle"},
    "player": {"de": "Spieler", "en": "Player"},
    "result": {"de": "Ergebnis", "en": "Result"},
    "no_results": {"de": "Noch keine Ergebnisse.", "en": "No results yet."},
    "not_played": {"de": "noch nicht gespielt", "en": "not played yet"},
    "play_first": {
        "de": "Spiel dieses Rätsel zuerst, um die Ergebnisse der anderen zu sehen.",
        "en": "Play this puzzle first to see the others' results.",
    },
    "all_puzzles": {"de": "Alle Rätsel", "en": "All puzzles"},
    "older": {"de": "Ältere", "en": "Older"},
    "newer": {"de": "Neuere", "en": "Newer"},
    # Submit
    "submit_title": {"de": "Ergebnis eintragen", "en": "Submit a result"},
    "submit_help": {
        "de": "Kopiere den Teilen-Text aus dem Spiel und füge ihn hier ein. Das Spiel wird automatisch erkannt.",
        "en": "Copy the share text from the game and paste it here. The game is detected automatically.",
    },
    "submit_button": {"de": "Eintragen", "en": "Submit"},
    "unknown_game": {
        "de": "Diesen Text konnte ich keinem Spiel zuordnen.",
        "en": "I couldn't match this text to any game.",
    },
    "saved": {"de": "{game} #{puzzle} gespeichert: {summary}", "en": "Saved {game} #{puzzle}: {summary}"},
    "already_submitted": {
        "de": "Du hast {game} #{puzzle} schon eingetragen.",
        "en": "You already submitted {game} #{puzzle}.",
    },
    "delete": {"de": "Löschen", "en": "Delete"},
    "deleted": {"de": "Ergebnis gelöscht.", "en": "Result deleted."},
    "confirm_delete": {"de": "Wirklich löschen?", "en": "Really delete?"},
    "show_share_text": {"de": "Teilen-Text anzeigen", "en": "Show share text"},
    # Stats
    "stats_title": {"de": "Statistiken", "en": "Statistics"},
    "played": {"de": "Gespielt", "en": "Played"},
    "solved": {"de": "Gelöst", "en": "Solved"},
    "average": {"de": "Durchschnitt", "en": "Average"},
    "best": {"de": "Bestes", "en": "Best"},
    "streak": {"de": "Serie", "en": "Streak"},
    "best_streak": {"de": "Beste Serie", "en": "Best streak"},
    "distribution": {"de": "Verteilung", "en": "Distribution"},
    "score_wordle": {"de": "Versuche", "en": "guesses"},
    "score_connections": {"de": "Fehler", "en": "mistakes"},
    "score_strands": {"de": "Hinweise", "en": "hints"},
    "score_travle": {"de": "Extra-Versuche", "en": "extra guesses"},
    "score_krillion": {"de": "Punkte", "en": "score"},
    "stats_help": {
        "de": "Serie = gelöste Rätsel mit aufeinanderfolgenden Nummern. Durchschnitt nur über gelöste Rätsel.",
        "en": "Streak = solved puzzles with consecutive numbers. Average over solved puzzles only.",
    },
    # Settings
    "settings_title": {"de": "Einstellungen", "en": "Settings"},
    "language": {"de": "Sprache", "en": "Language"},
    "hide_spoilers": {"de": "Spoiler verbergen", "en": "Hide spoilers"},
    "hide_spoilers_help": {
        "de": "Ergebnisse der anderen erst anzeigen, wenn ich das Rätsel selbst eingetragen habe.",
        "en": "Only show the others' results once I have submitted the puzzle myself.",
    },
    "save": {"de": "Speichern", "en": "Save"},
    "settings_saved": {"de": "Einstellungen gespeichert.", "en": "Settings saved."},
    "change_password": {"de": "Passwort ändern", "en": "Change password"},
    "current_password": {"de": "Aktuelles Passwort", "en": "Current password"},
    "new_password": {"de": "Neues Passwort", "en": "New password"},
    "password_changed": {"de": "Passwort geändert.", "en": "Password changed."},
    "password_wrong": {"de": "Aktuelles Passwort ist falsch.", "en": "Current password is wrong."},
    "password_too_short": {
        "de": "Das Passwort muss mindestens 8 Zeichen lang sein.",
        "en": "The password must be at least 8 characters long.",
    },
    # Admin
    "admin_title": {"de": "Benutzer verwalten", "en": "Manage users"},
    "create_user": {"de": "Benutzer anlegen", "en": "Create user"},
    "is_admin": {"de": "Admin", "en": "Admin"},
    "user_created": {"de": "Benutzer {name} angelegt.", "en": "User {name} created."},
    "user_exists": {"de": "Diesen Benutzernamen gibt es schon.", "en": "That username already exists."},
    "reset_password": {"de": "Passwort zurücksetzen", "en": "Reset password"},
    "password_reset_done": {
        "de": "Neues Passwort für {name}: {password}",
        "en": "New password for {name}: {password}",
    },
    "delete_user": {"de": "Benutzer löschen", "en": "Delete user"},
    "user_deleted": {"de": "Benutzer {name} gelöscht.", "en": "User {name} deleted."},
    "cannot_delete_self": {"de": "Du kannst dich nicht selbst löschen.", "en": "You can't delete yourself."},
    "results_count": {"de": "Ergebnisse", "en": "Results"},
    "leave_empty_generate": {
        "de": "Leer lassen, um ein zufälliges Passwort zu erzeugen.",
        "en": "Leave empty to generate a random password.",
    },
}


def get_language():
    """The logged-in user's language, otherwise the one picked on the login page."""
    if current_user.is_authenticated:
        return current_user.language
    return session.get("language", DEFAULT_LANGUAGE)


def translate(key, **values):
    entry = TEXTS.get(key)
    if entry is None:
        return key  # makes missing translations easy to spot on the page
    text = entry.get(get_language()) or entry[DEFAULT_LANGUAGE]
    return text.format(**values) if values else text
