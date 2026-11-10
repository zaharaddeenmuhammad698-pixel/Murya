"""
Add the optional Supabase (Postgres) database to YOUR OWN app.py or ussd.py. Nothing else in the file is touched.

After this change:
  - if a secret/environment value called DATABASE_URL is set, the file stores its data in Supabase through pgcompat.py;
  - if DATABASE_URL is empty or missing, it keeps using the local SQLite file exactly as before.
So you can switch Supabase on and off just by adding or removing DATABASE_URL.

app.py also gets two small extras: set-up steps run once per server instead of on every page refresh (a remote database
would be slow otherwise), and one sentence in the privacy note saying messages may be stored in a Supabase database.

Use (in VS Code: Terminal > New Terminal, in the folder that holds the file):
    python apply_supabase_option.py app.py
    python apply_supabase_option.py ussd.py
Also put pgcompat.py next to the file, and add  psycopg2-binary  to its requirements.txt.

It saves a backup first (<file>.bak), keeps your line endings, checks the result is valid Python, and only then saves.
All or nothing: if a main spot is not found, nothing is changed.
"""
import re
import shutil
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "app.py"
raw = open(path, "rb").read().decode("utf-8")
crlf = "\r\n" in raw
text = raw.replace("\r\n", "\n")

if "pgcompat" in text:
    print("This file already has the Supabase option. Nothing was changed.")
    sys.exit(0)

problems = []
APP_MODE = "def _conn():" in text
USSD_MODE = "def db():" in text and "murya_ussd.db" in text

if APP_MODE:
    old_conn = ('def _conn():\n    c = sqlite3.connect(DB, timeout=10)\n    c.row_factory = sqlite3.Row\n'
                '    c.execute("PRAGMA journal_mode=WAL")\n    return c\n')
    new_conn = '''DATABASE_URL = secret("DATABASE_URL", "")   # set it to store data in Supabase (Postgres); leave it empty to use the local SQLite file

@st.cache_resource
def _done_flags(): return set()
def _once(name, fn):
    """With a remote database, run each set-up step once per server process instead of on every page refresh."""
    if not DATABASE_URL: return fn()
    flags = _done_flags()
    if name not in flags:
        fn(); flags.add(name)

def _conn():
    if DATABASE_URL:
        import pgcompat
        return pgcompat.connect(DATABASE_URL)
    c = sqlite3.connect(DB, timeout=10)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL")
    return c
'''
    if text.count(old_conn) == 1: text = text.replace(old_conn, new_conn)
    else: problems.append("the _conn function")
    for call in ("init_db", "sec_init", "pu_init", "redact_existing"):
        text, n = re.subn(rf"(?m)^{call}\(\)$", f'_once("{call}", {call})', text, count=1)
        if not n: problems.append(f"the {call}() line")
    # one sentence in the privacy note (optional)
    text = re.sub(r"(<p><b>Outside services:</b>[^\n]*?)(</p>)",
                  lambda m: m.group(1) + " Messages are stored on the app's own server or, if the cloud-database option is on, in a Supabase database that may be outside Nigeria." + m.group(2),
                  text, count=1)
    text = re.sub(r"(<p><b>Hidimomin waje:</b>[^\n]*?)(</p>)",
                  lambda m: m.group(1) + " Ana adana saƙonni a uwar garken manhajar ko, idan an kunna zaɓin ma'ajiyar gajimare, a ma'ajiyar Supabase wadda za ta iya kasancewa a wajen Najeriya." + m.group(2),
                  text, count=1)
elif USSD_MODE:
    old_db = ('def db():\n    c = sqlite3.connect(DB_PATH, timeout=10)\n    c.row_factory = sqlite3.Row\n'
              '    c.execute("PRAGMA journal_mode=WAL")\n    return c\n')
    new_db = '''DATABASE_URL = os.environ.get("DATABASE_URL", "")   # set it to store data in Supabase (Postgres); leave it empty to use the local SQLite file

def db():
    if DATABASE_URL:
        import pgcompat
        return pgcompat.connect(DATABASE_URL)
    c = sqlite3.connect(DB_PATH, timeout=10)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL")
    return c
'''
    if text.count(old_db) == 1: text = text.replace(old_db, new_db)
    else: problems.append("the db function")
else:
    problems.append("a database function (this does not look like app.py or ussd.py)")

if problems:
    print("Nothing was changed. These parts were not found:", ", ".join(problems))
    print("Your file looks different from what I expected. Send me those parts and I will adjust the fix.")
    sys.exit(1)

try:
    compile(text, path, "exec")
except SyntaxError as e:
    print("Stopped: the result would not be valid Python (line", e.lineno, "). Your file was NOT changed.")
    sys.exit(1)

shutil.copyfile(path, path + ".bak")
out = text.replace("\n", "\r\n") if crlf else text
with open(path, "wb") as f:
    f.write(out.encode("utf-8"))
print("Done. Backup saved as", path + ".bak")
print("Next: put pgcompat.py next to this file, add psycopg2-binary to requirements.txt, and make sure DATABASE_URL is set.")
