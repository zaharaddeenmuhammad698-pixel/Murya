"""
Copy your existing MURYA data from the SQLite files into Supabase. Run it once, on your own computer.

    set DATABASE_URL=...            (Windows: set DATABASE_URL=postgresql://...   Mac/Linux: export DATABASE_URL=...)
    python migrate_sqlite_to_supabase.py murya.db                       (web app data)
    python migrate_sqlite_to_supabase.py murya_ussd.db                  (USSD data, if you have any worth keeping)
    python migrate_sqlite_to_supabase.py murya.db --dry-run             (only counts the rows; changes nothing)

It makes the tables if they are missing, skips any table that already has rows (add --force to copy anyway),
copies the rows with their ids, and fixes the id counters. It does not copy audio files (voice_notes/ and voice_audio/).
The login-attempts table is not copied.
Needs:  pip install psycopg2-binary
"""
import os
import re
import sqlite3
import sys

import pgcompat

ALLOWED = ["questions", "kb", "polling_units", "pu_meta", "audit_log", "reports"]
args = [a for a in sys.argv[1:] if not a.startswith("--")]
dry, force = "--dry-run" in sys.argv, "--force" in sys.argv
if not args:
    print(__doc__); sys.exit(1)
src_path = args[0]
if not os.path.exists(src_path):
    print("I cannot find", src_path); sys.exit(1)
src = sqlite3.connect(src_path)
tables = {r[0]: r[1] for r in src.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
todo = [t for t in ALLOWED if t in tables]
print("Tables to copy from", src_path + ":", ", ".join(todo) or "none")
for t in todo:
    print(f"  {t}: {src.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]} rows")
if dry or not todo:
    print("Dry run: nothing was changed." if dry else "Nothing to copy."); sys.exit(0)

url = os.environ.get("DATABASE_URL", "")
if not url:
    print("DATABASE_URL is not set. See the top of this file."); sys.exit(1)

for t in todo:
    create = tables[t]
    if not re.search(r"IF\s+NOT\s+EXISTS", create, re.I):
        create = re.sub(r"CREATE\s+TABLE\s+", "CREATE TABLE IF NOT EXISTS ", create, count=1, flags=re.I)
    with pgcompat.connect(url) as c:
        c.execute(create)
        have = c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    if have and not force:
        print(f"  {t}: already has {have} rows in Supabase, skipped (use --force to copy anyway)"); continue
    cur = src.execute(f"SELECT * FROM {t}")
    cols = [d[0] for d in cur.description]
    sql = f"INSERT INTO {t}({','.join(cols)}) VALUES({','.join('?' * len(cols))})"
    copied = 0
    while True:
        batch = cur.fetchmany(500)
        if not batch: break
        with pgcompat.connect(url) as c:
            c.executemany(sql, batch)
        copied += len(batch)
    if "id" in cols:
        with pgcompat.connect(url) as c:
            c.execute(f"SELECT setval(pg_get_serial_sequence('{t}','id'), COALESCE((SELECT MAX(id) FROM {t}), 1), (SELECT COUNT(*) FROM {t}) > 0)")
    print(f"  {t}: copied {copied} rows")
print("Done. Now run supabase_security.sql in the Supabase SQL editor.")
