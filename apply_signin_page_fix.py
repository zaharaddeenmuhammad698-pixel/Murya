"""
Fix the dashboard sign-in loop in YOUR OWN ussd.py. Nothing else in your file is touched.

The old sign-in used the browser's pop-up box (HTTP Basic login). Phones often fail to remember it, so you are asked again and again,
and the page never says what is wrong. This fix gives the dashboard a normal sign-in page. You stay signed in with a cookie for 12 hours,
and the page tells you clearly when the user name or password is wrong, when the password setting on the server is damaged,
or when the browser blocked the cookie. It is forgiving about phone keyboards: capital letters in the user name do not matter,
and a space added at the end of the password is ignored. Quote marks pasted around the stored hash are ignored too.

Use (in VS Code: Terminal > New Terminal, in the folder that holds ussd.py):
    python apply_signin_page_fix.py              (fixes ussd.py in this folder)
    python apply_signin_page_fix.py path\\to\\ussd.py

It saves a backup first (ussd.py.bak), keeps your line endings, checks the result is valid Python, and only then saves.
"""
import re
import shutil
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "ussd.py"
raw = open(path, "rb").read().decode("utf-8")
crlf = "\r\n" in raw
text = raw.replace("\r\n", "\n")

if "def _hash_problem" in text:
    print("Your file already has the sign-in page. Nothing was changed.")
    sys.exit(0)

NEW = '''from flask import redirect

SESSION_HOURS = 12
_H = (ADMIN_PASSWORD_HASH or "").strip().strip('"').strip("'").strip()   # ignore quote marks pasted around the hash

def _hash_problem():
    """A plain-English hint when ADMIN_PASSWORD_HASH was pasted wrongly (never shows the value itself)."""
    if not _H:
        return "ADMIN_PASSWORD_HASH is not set in the Environment page (check the spelling of the name, then redeploy)."
    if any(c in _H for c in " \\t\\r\\n") or not _H.startswith(("scrypt:", "pbkdf2:")) or _H.count("$") != 2:
        return ("ADMIN_PASSWORD_HASH looks damaged. It must be ONE line that starts with scrypt: or pbkdf2:, with no spaces. "
                "Make it again with make_ussd_secrets.py and paste the whole value after the = sign.")
    return ""

LOGIN_PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>MURYA sign in</title><style>body{font-family:Arial,sans-serif;background:#f5f5f5;padding:16px;color:#14261b}
.card{max-width:420px;margin:30px auto;background:#fff;padding:22px;border-radius:14px}h1{color:#0a7e07;font-size:22px;margin-top:0}
label{display:block;margin:12px 0 4px;font-weight:bold}input{width:100%;padding:12px;font-size:16px;border:1px solid #888;border-radius:8px;box-sizing:border-box}
.btn{margin-top:16px;width:100%;background:#0a7e07;color:#fff;padding:13px;font-size:16px;border:none;border-radius:10px;cursor:pointer}
.err{background:#fee2e2;color:#991b1b;padding:10px;border-radius:8px;margin:10px 0}.warn{background:#fef3c7;color:#92400e;padding:10px;border-radius:8px;margin:10px 0}</style></head>
<body><div class="card"><h1>MURYA reports: sign in</h1>
{% if problem %}<div class="warn">{{ problem }}</div>{% endif %}
{% if error %}<div class="err">{{ error }}</div>{% endif %}
<form method="post" action="/login"><input type="hidden" name="csrf" value="{{ csrf }}">
<label for="u">User name</label><input id="u" name="username" autocomplete="username" autocapitalize="none" autocorrect="off" required>
<label for="p">Password</label><input id="p" name="password" type="password" autocomplete="current-password" required>
<button class="btn" type="submit">Sign in</button></form></div></body></html>"""

@app.route("/login", methods=["GET", "POST"])
def login():
    problem, error = _hash_problem(), ""
    if request.method == "POST":
        who, t = _client(), time.time()
        _fails[who] = [x for x in _fails.get(who, []) if t - x < 300]
        if not hmac.compare_digest(request.form.get("csrf", ""), session.get("csrf", "x")):
            error = "Your browser did not keep the sign-in cookie. Allow cookies for this site, open the page again, and retry."
        elif len(_fails[who]) >= 8:
            error = "Too many wrong attempts. Try again in 5 minutes."
        elif problem:
            error = "The password setting on the server is not correct (see the yellow note)."
        else:
            u, p = request.form.get("username", "").strip().lower(), request.form.get("password", "")
            user_ok = hmac.compare_digest(u.encode(), ADMIN_USER.strip().lower().encode())
            pass_ok = check_password_hash(_H, p) or (p != p.strip() and check_password_hash(_H, p.strip()))
            if user_ok and pass_ok:
                session.clear(); session["admin"] = True; session["t"] = t
                return redirect("/dashboard")
            _fails[who].append(t)
            error = "Wrong user name or password. The user name is " + ("the ADMIN_USER value in your Environment page." if os.environ.get("ADMIN_USER") else "admin.")
    return render_template_string(LOGIN_PAGE, problem=problem, error=error, csrf=csrf_token())

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect("/login")

def require_admin(f):
    @wraps(f)
    def wrapper(*a, **k):
        if session.get("admin") and time.time() - session.get("t", 0) < SESSION_HOURS * 3600:
            return f(*a, **k)
        session.pop("admin", None)
        if request.method == "GET": return redirect("/login")
        return Response("Please sign in again.", 401)
    return wrapper
'''

pattern = r'def require_admin\(f\):\n(?:[ \t]+[^\n]*\n|\n)*?    return wrapper\n'
new_text, n = re.subn(pattern, lambda m: NEW, text, count=1)
if not n:
    print("Nothing was changed: I could not find the function require_admin in your file.")
    print("Send me the lines from 'def require_admin' to 'return wrapper' and I will adjust the fix.")
    sys.exit(1)

# a Log out button on the dashboard (optional: skipped if the heading is not found)
new_text, k = re.subn(r'(<div class="card">)(<h1>MURYA questions and reports)',
                      lambda m: m.group(1) + '<form action="/logout" method="post" style="float:right"><button class="btn" type="submit">Log out</button></form>' + m.group(2),
                      new_text, count=1)

try:
    compile(new_text, path, "exec")
except SyntaxError as e:
    print("Stopped: the result would not be valid Python (line", e.lineno, "). Your file was NOT changed.")
    sys.exit(1)

shutil.copyfile(path, path + ".bak")
out = new_text.replace("\n", "\r\n") if crlf else new_text
with open(path, "wb") as f:
    f.write(out.encode("utf-8"))
print("Done. Backup saved as", path + ".bak")
print("Added: a sign-in page at /login" + (", and a Log out button." if k else "."))
print("Commit ussd.py, redeploy, then open https://YOUR-APP/dashboard. It sends you to the sign-in page.")
