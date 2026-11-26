# DISCLAIMER

This is completely vibe-coded by Claude Opus 5.5 (Medium)

# Dailies

A small Flask website where a group of friends paste the share texts of daily
browser games (Wordle, Connections, Strands, Travle, krillion) and compare
their results per puzzle.

- Accounts are created by the admin; there is no public sign-up.
- Paste a share text, and the game and puzzle number are detected automatically.
- **No spoilers** (on by default, can be switched off in the settings): you
  only see the others' results for a puzzle once you have submitted your own.
- Per-player stats: solve rate, average, best, streaks, score distribution.
- German / English interface.

## How the code is organised

```
app/
  __init__.py      App setup: config, database, login, CLI commands
  models.py        Database tables: User and Result
  games/           One file per game; each knows how to parse its share text
    base.py        The Game base class every game builds on
    __init__.py    List of all games + detect() which finds the right one
  main.py          Pages: overview, submit, game history, puzzle, stats
  auth.py          Login, logout, settings
  admin.py         Create / reset / delete user accounts
  i18n.py          German and English texts
  templates/       HTML (Jinja templates)
  static/style.css Styling (light + dark mode)
tests/             Run with: pytest
deploy/            systemd service, Caddy/Nginx config, backup script
```

A good order to read it in is `games/wordle.py` → `models.py` → `main.py` →
`templates/index.html`.

### Adding a new game

1. Copy `app/games/wordle.py` to `app/games/newgame.py` and adapt `slug`,
   `name`, `url`, `parse()` and `summary()`.
2. Add it to the list in `app/games/__init__.py`.
3. Add a `score_<slug>` entry in `app/i18n.py` (the label on the stats page).
4. Add a test with a real share text to `tests/test_parsers.py`.

### Fixing a parser

Every result keeps the original pasted text. After changing a parser, run
`flask --app app reparse` and all stored results are re-parsed.

## Running locally

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/flask --app app create-user user --admin
.venv/bin/flask --app app run --debug
```

Then open http://127.0.0.1:5000. Run the tests with
`.venv/bin/pip install pytest && .venv/bin/pytest`.

## Deployment (Debian/Ubuntu VM on Proxmox)

The setup: **Gunicorn** runs the Flask app, **systemd** keeps it running, and
**Caddy** (or Nginx) handles HTTPS in front of it. The data lives in a single
SQLite file.

```bash
# 1. System packages and a dedicated user
sudo apt install python3 python3-venv git sqlite3
sudo useradd --system --home /opt/dailies --shell /usr/sbin/nologin dailies

# 2. Code and dependencies
sudo git clone https://github.com/usayaa/dailies-comparer.git /opt/dailies
sudo python3 -m venv /opt/dailies/.venv
sudo /opt/dailies/.venv/bin/pip install -r /opt/dailies/requirements.txt
sudo mkdir -p /opt/dailies/instance
sudo chown -R dailies:dailies /opt/dailies

# 3. Configuration (edit SECRET_KEY!)
sudo cp /opt/dailies/deploy/dailies.env.example /etc/dailies.env
sudo chmod 600 /etc/dailies.env
sudo nano /etc/dailies.env

# 4. Start the service
sudo cp /opt/dailies/deploy/dailies.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now dailies

# 5. Create your admin account
cd /opt/dailies
sudo -u dailies .venv/bin/flask --app app create-user user --admin
```

(If you set a custom `DATABASE_URL` in `/etc/dailies.env`, pass it here too:
`sudo -u dailies env DATABASE_URL=... .venv/bin/flask ...`.)

**HTTPS:** point the DNS record for `example.domain.com` to your server, then use
`deploy/Caddyfile` (Caddy fetches the certificate itself) or
`deploy/nginx.conf` + certbot. If the proxy runs on a different VM, change
`--bind 127.0.0.1:8000` in the service file to `0.0.0.0:8000` and only allow
port 8000 from the proxy's IP.

Then log in, open **Verwaltung / Admin** and create accounts for your
friends. A random password is generated and shown once.

**Updates:**

```bash
cd /opt/dailies && sudo -u dailies git pull
sudo -u dailies .venv/bin/pip install -r requirements.txt
sudo systemctl restart dailies
```

**Backups:** `deploy/backup.sh` makes a daily copy of the database; add it to
the `dailies` user's crontab (`sudo crontab -u dailies -e`). Proxmox VM
backups work too.

**Logs:** `journalctl -u dailies -f`
