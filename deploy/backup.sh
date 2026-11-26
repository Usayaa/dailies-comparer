#!/bin/sh
# Daily SQLite backup, keeps 30 days. Run from cron as the dailies user, e.g.
#   15 4 * * * /opt/dailies/deploy/backup.sh
set -e
mkdir -p /opt/dailies/backups
sqlite3 /opt/dailies/instance/dailies.sqlite ".backup /opt/dailies/backups/dailies-$(date +%F).sqlite"
find /opt/dailies/backups -name 'dailies-*.sqlite' -mtime +30 -delete
