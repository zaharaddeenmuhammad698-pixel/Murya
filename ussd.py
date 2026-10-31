"""
MURYA USSD / SMS service (Africa's Talking)

A citizen dials the USSD code, picks a language, then either asks a question (verified answers on the phone screen, or a typed
question for a reviewer) or reports a problem at a polling unit. A reviewer reads the messages on a password-protected
dashboard and replies by SMS from the sender name MURYA.

Run on Render (or anywhere):   gunicorn ussd:app --workers 1 --threads 4
Environment variables (all secret values go in the host's Environment page, never in this file):
  AT_USERNAME, AT_API_KEY      Africa's Talking (username is "sandbox" for the simulator)
  AT_SENDER_ID                 default MURYA (must be registered with the operators for live use)
  ADMIN_USER                   dashboard user name (default "admin")
  ADMIN_PASSWORD_HASH          made with:  python -c "from werkzeug.security import generate_password_hash as g; print(g('YOUR LONG PASSPHRASE'))"
  USSD_TOKEN                   a long random string; put it in the callback URL:  https://YOUR-APP/murya/<USSD_TOKEN>
  SECRET_KEY                   a long random string (signs the login-form tokens)
  DB_PATH, RETENTION_DAYS, MAX_REPORTS_PER_HOUR, COOKIE_SECURE   optional
Use only test data in the simulator. Do not point this at a live election.
"""
import csv, hashlib, hmac, io, json, os, re, sqlite3, secrets, time
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, Response, abort, render_template_string, request, session
from werkzeug.security import check_password_hash

app = Flask(__name__)

AT_USERNAME = os.environ.get("AT_USERNAME")
AT_API_KEY = os.environ.get("AT_API_KEY")
AT_SENDER_ID = os.environ.get("AT_SENDER_ID", "MURYA")
ADMIN_USER = os.environ.get("ADMIN_USER", "admin")
ADMIN_PASSWORD_HASH = os.environ.get("ADMIN_PASSWORD_HASH", "")
USSD_TOKEN = os.environ.get("USSD_TOKEN", "")
DB_PATH = os.environ.get("DB_PATH", "murya_ussd.db")
OLD_JSON = os.environ.get("REPORTS_FILE", "reports.json")
RETENTION_DAYS = int(os.environ.get("RETENTION_DAYS", "30"))
MAX_REPORTS_PER_HOUR = int(os.environ.get("MAX_REPORTS_PER_HOUR", "5"))

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or hashlib.sha256(("murya|" + ADMIN_PASSWORD_HASH).encode()).hexdigest()
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.environ.get("COOKIE_SECURE", "1") == "1"   # set COOKIE_SECURE=0 only for local http testing

# ---- Africa's Talking SMS (only if keys exist, so USSD still works without them) ----
sms = None
if AT_USERNAME and AT_API_KEY:
    try:
        import africastalking
        africastalking.initialize(AT_USERNAME, AT_API_KEY)
        sms = africastalking.SMS
        print(f"Africa's Talking ready as {AT_USERNAME}")
    except Exception as e:
        print(f"Africa's Talking could not start: {type(e).__name__}")
else:
    print("No Africa's Talking keys: USSD works, SMS replies are off")
if not USSD_TOKEN:
    print("WARNING: USSD_TOKEN is not set, so anyone can post fake reports to /murya. Set it and use /murya/<token>.")
if not ADMIN_PASSWORD_HASH:
    print("WARNING: ADMIN_PASSWORD_HASH is not set, so the dashboard is switched off.")

# ---- Database (SQLite: safe for several requests at once, unlike a JSON file) ----
def db():
    c = sqlite3.connect(DB_PATH, timeout=10)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL")
    return c

def init_db():
    with db() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS reports(
            id INTEGER PRIMARY KEY AUTOINCREMENT, created TEXT, phone TEXT, pu TEXT, issue_type TEXT,
            issue TEXT, lang TEXT, status TEXT DEFAULT 'NEW', replied_at TEXT DEFAULT '')""")

def now(): return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def purge_old():
    cutoff = (datetime.now() - timedelta(days=RETENTION_DAYS)).strftime("%Y-%m-%d %H:%M:%S")
    with db() as c: c.execute("DELETE FROM reports WHERE created < ?", (cutoff,))

# ---- Privacy helpers ----
_REDACT = [
    (re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+"), "[email removed]"),
    (re.compile(r"(?<![\w/])\+?\d(?:[\s.\-]?\d){9,}(?![\w/])"), "[number removed]"),
    (re.compile(r"\b(?=[A-Za-z0-9]*\d)(?=[A-Za-z0-9]*[A-Za-z])[A-Za-z0-9]{15,}\b"), "[number removed]"),
]
def redact(text):
    for pat, rep in _REDACT: text = pat.sub(rep, text)
    return text

def clean_text(text, limit):
    text = re.sub(r"[\x00-\x1f\x7f]", " ", text or "")
    return redact(text).strip()[:limit]

def mask_phone(p): return (p[:4] + "****" + p[-3:]) if p and len(p) > 8 else "****"
def phone_id(p): return hashlib.sha256((app.config["SECRET_KEY"] + (p or "")).encode()).hexdigest()[:10]

def migrate_old_json():
    """One-off: move reports from the old reports.json into the database, removing numbers from the text."""
    if not os.path.exists(OLD_JSON): return
    with db() as c:
        if c.execute("SELECT COUNT(*) FROM reports").fetchone()[0]: return
        try:
            with open(OLD_JSON) as f: data = json.load(f)
        except Exception:
            return
        for r in data:
            c.execute("INSERT INTO reports(created,phone,pu,issue_type,issue,lang) VALUES(?,?,?,?,?,?)",
                      (r.get("time") or now(), r.get("phone", ""), str(r.get("pu", ""))[:20], str(r.get("issue_type", ""))[:30],
                       clean_text(r.get("issue", ""), 300), r.get("language", "")))
    os.replace(OLD_JSON, OLD_JSON + ".migrated")      # delete this file once you have checked the dashboard

init_db(); migrate_old_json(); purge_old()

# ---- USSD ----
# Keep every screen in plain ASCII (no hooked Hausa letters): phones switch to a much shorter character limit otherwise.
ISSUES = {"1": "BVAS failure", "2": "Late materials", "3": "Vote buying", "4": "Violence", "5": "No EC8A", "6": "Other"}

# INEC office addresses (checked in person). Keep in step with the verified answers in the MURYA web app.
LGA_OFFICES = {
    "Alkaleri": "Along Bauchi Road, Alkaleri",
    "Bauchi (Kofar Ran)": "Opposite Urban Maternity, Adamu Ajiya Road, Bauchi",
    "Bogoro": "Adjacent LGA Secretariat, Bogoro",
    "Dambam": "Off Kano-Maiduguri Road, Dambam",
    "Darazo": "Near V.I.O. Office, Darazo",
    "Dass": "Along Dunkurma Street, opposite Library, Dass",
    "Gamawa": "Opposite Gamawa LGA Secretariat, Gamawa",
    "Ganjuwa": "Along Kano Road, Kafin Madaki",
    "Giade": "Along Kano Road, Giade",
    "Itas/Gadau": "Along Atafowa Road, Itas",
    "Jama'are": "Near Water Board, Jama'are",
    "Katagum": "Along Azare-Bulkachuwa Road, Azare",
    "Kirfi": "Adjacent Kirfi Police Station, Kirfi",
    "Misau": "Along Kari Road, Misau",
    "Ningi": "Opposite Ningi Police Station, along Kano Road, Ningi",
    "Shira": "Along Giade-Misau Road, Shira",
    "Tafawa Balewa": "Beside DSS Office, Bununu",
    "Toro": "LGA Secretariat Road, near First Bank, Toro",
    "Warji": "Unguwar Gandu (Makera), opposite Warji Micro-Finance Bank, Warji",
    "Zaki": "Old Secretariat, Katagum, adjacent Zaki LGA Secretariat",
}
LGA_NAMES = list(LGA_OFFICES)
PAGE_SIZE = 6

# Verified answers (same facts as the web app). Re-check the dates at inec.gov.ng before any launch.
ANSWERS = {
    "en": {
        "dates": "END Presidential and National Assembly: 16 Jan 2027. Governorship and State Assembly: 6 Feb 2027. Confirm at inec.gov.ng.",
        "photo": "END No. You need your original PVC. A phone photo or photocopy does not work. Confirm at inec.gov.ng or your INEC office.",
        "check": "END Go to inec.gov.ng or visit the INEC office nearest to you in Bauchi to check your PVC.",
        "office": "END INEC office, {name}: {addr}. Confirm at inec.gov.ng.",
    },
    "ha": {
        "dates": "END Shugaban kasa da Majalisar Tarayya: 16 ga Janairu 2027. Gwamnoni da Majalisun Jihohi: 6 ga Fabrairu 2027. Tabbatar a inec.gov.ng.",
        "photo": "END A'a. Dole ne ka kasance da katin zabe na asali. Hoton waya ko photocopy ba ya aiki. Tabbatar a inec.gov.ng ko ofishin INEC.",
        "check": "END Je inec.gov.ng ko ofishin INEC mafi kusa da kai a Bauchi don duba katinka.",
        "office": "END Ofishin INEC na {name}: {addr}. Tabbatar a inec.gov.ng.",
    },
}
MSG = {
    "lang":   "CON MURYA - Bauchi\n1. English\n2. Hausa",
    "main_en": "CON MURYA\n1. Ask a question\n2. Report a problem",
    "main_ha": "CON MURYA\n1. Yi tambaya\n2. Bayar da rahoto",
    "ask_en": "CON Ask a question:\n1. Election dates\n2. INEC office in my LGA\n3. Photocopy of my PVC?\n4. How to check my PVC\n5. Something else",
    "ask_ha": "CON Yi tambaya:\n1. Ranakun zabe\n2. Ofishin INEC na karamar hukumata\n3. Hoton katina?\n4. Yadda zan duba katina\n5. Wani abu daban",
    "q_en": "CON Type your question. Do not write names or phone numbers. We keep it 30 days:",
    "q_ha": "CON Rubuta tambayarka. Kada ka rubuta suna ko lambar waya. Ana ajiye ta kwana 30:",
    "qok_en": "END Thanks! A reviewer will reply by SMS if they can.",
    "qok_ha": "END Nagode! Mai dubawa zai aiko amsa ta SMS idan ya samu dama.",
    "bad_en": "END That choice is not valid. Please dial again.",
    "bad_ha": "END Zabin bai yi daidai ba. Sake kira, don Allah.",
    "pu_en":  "CON Enter polling unit code (e.g. 05-04-02-001), or 0 if you do not know it:",
    "pu_ha":  "CON Rubuta lambar rumfar zabe (misali 05-04-02-001), ko 0 idan ba ka sani ba:",
    "issue_en": "CON Select issue:\n1. BVAS failure\n2. Late materials\n3. Vote buying\n4. Violence\n5. No EC8A\n6. Other",
    "issue_ha": "CON Zabi matsala:\n1. BVAS lalace\n2. Kayan sun makara\n3. Sayen kuri'a\n4. Tashin hankali\n5. Babu EC8A\n6. Sauran",
    "desc_en": "CON Describe the problem. Do not write names or phone numbers. We keep it 30 days:",
    "desc_ha": "CON Bayyana matsalar. Kada ka rubuta suna ko lambar waya. Ana ajiye ta kwana 30:",
    "many_en": "END Too many messages from this number. Please try again later.",
    "many_ha": "END Sakonni sun yi yawa daga wannan lamba. A sake gwadawa nan gaba.",
    "ok_en": "END Thanks! Report received. PU: {pu}. A reviewer may reply by SMS.",
    "ok_ha": "END Nagode! Mun karbi rahoton. PU: {pu}. Mai dubawa na iya aiko amsa ta SMS.",
}

def normalise_pu(raw):
    s = re.sub(r"[\s/_.]+", "-", (raw or "").strip())
    if s == "0": return "unknown"
    return s if re.fullmatch(r"\d{2}-\d{2}-\d{2}-\d{3}", s) else None

def lga_menu(k, page):
    names = LGA_NAMES[page * PAGE_SIZE:(page + 1) * PAGE_SIZE]
    lines = [f"{i}. {n}" for i, n in enumerate(names, 1)]
    if (page + 1) * PAGE_SIZE < len(LGA_NAMES): lines.append("7. More" if k == "en" else "7. Kari")
    return ("CON Select your LGA:" if k == "en" else "CON Zabi karamar hukuma:") + "\n" + "\n".join(lines)

def office_flow(k, toks):
    """toks = what the caller typed after choosing 'INEC office'. Typing 7 shows the next page of LGAs."""
    page = 0
    for t in toks:
        names = LGA_NAMES[page * PAGE_SIZE:(page + 1) * PAGE_SIZE]
        more = (page + 1) * PAGE_SIZE < len(LGA_NAMES)
        if more and t == "7": page += 1; continue
        if t.isdigit() and 1 <= int(t) <= len(names):
            name = names[int(t) - 1]
            return ANSWERS[k]["office"].format(name=name, addr=LGA_OFFICES[name])
        return MSG["bad_" + k]
    return lga_menu(k, page)

def save_message(k, phone, pu, kind, details, done):
    """Store a question or a report (with the 5-per-hour limit) and return the closing screen."""
    with db() as c:
        recent = c.execute("SELECT COUNT(*) FROM reports WHERE phone=? AND created >= ?",
                           (phone, (datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"))).fetchone()[0]
        if recent >= MAX_REPORTS_PER_HOUR: return MSG["many_" + k]
        c.execute("INSERT INTO reports(created,phone,pu,issue_type,issue,lang) VALUES(?,?,?,?,?,?)",
                  (now(), phone, pu, kind, details, "English" if k == "en" else "Hausa"))
    return done.format(pu=pu)

def ask_flow(k, phone, rest):
    if not rest: return MSG["ask_" + k]
    c = rest[0]
    if c == "1": return ANSWERS[k]["dates"]
    if c == "2": return office_flow(k, rest[1:])
    if c == "3": return ANSWERS[k]["photo"]
    if c == "4": return ANSWERS[k]["check"]
    if c == "5":
        question = clean_text("*".join(rest[1:]), 300)
        if not question: return MSG["q_" + k]
        return save_message(k, phone, "n/a", "Question", question, MSG["qok_" + k])
    return MSG["bad_" + k]

def report_flow(k, phone, rest):
    if not rest: return MSG["pu_" + k]
    pu = normalise_pu(rest[0])
    if pu is None: return MSG["bad_" + k]
    if len(rest) == 1: return MSG["issue_" + k]
    if rest[1] not in ISSUES: return MSG["bad_" + k]
    if len(rest) == 2: return MSG["desc_" + k]
    details = clean_text("*".join(rest[2:]), 300)        # a "*" typed inside the description is kept
    if not details: return MSG["desc_" + k]
    return save_message(k, phone, pu, ISSUES[rest[1]], details, MSG["ok_" + k])

def ussd_logic(phone, text):
    parts = text.split("*") if text else []
    if not parts: return MSG["lang"]
    if parts[0] not in ("1", "2"): return MSG["bad_en"] + "\n" + MSG["bad_ha"][4:]
    k = "en" if parts[0] == "1" else "ha"
    if len(parts) == 1: return MSG["main_" + k]
    if parts[1] == "1": return ask_flow(k, phone, parts[2:])
    if parts[1] == "2": return report_flow(k, phone, parts[2:])
    return MSG["bad_" + k]

@app.route("/murya", methods=["POST"])
@app.route("/murya/<token>", methods=["POST"])
def ussd(token=""):
    if USSD_TOKEN and not hmac.compare_digest(token, USSD_TOKEN): abort(404)
    reply = ussd_logic(request.values.get("phoneNumber", ""), request.values.get("text", "") or "")
    return Response(reply, mimetype="text/plain")

# ---- Admin dashboard ----
_fails = {}   # per-worker memory: wrong dashboard logins per address
def _client(): return (request.headers.get("X-Forwarded-For", request.remote_addr or "") or "").split(",")[0].strip()

def require_admin(f):
    @wraps(f)
    def wrapper(*a, **k):
        if not ADMIN_PASSWORD_HASH:
            return Response("Dashboard is off: set ADMIN_PASSWORD_HASH in the Environment page.", 503)
        who, t = _client(), time.time()
        _fails[who] = [x for x in _fails.get(who, []) if t - x < 300]
        if len(_fails[who]) >= 8:
            return Response("Too many wrong attempts. Try again in 5 minutes.", 429)
        auth = request.authorization
        ok = bool(auth) and hmac.compare_digest(auth.username or "", ADMIN_USER) and check_password_hash(ADMIN_PASSWORD_HASH, auth.password or "")
        if not ok:
            if auth: _fails[who].append(t)
            return Response("Sign in required", 401, {"WWW-Authenticate": 'Basic realm="MURYA admin"'})
        return f(*a, **k)
    return wrapper

def csrf_token():
    if "csrf" not in session: session["csrf"] = secrets.token_urlsafe(24)
    return session["csrf"]
def check_csrf():
    if not hmac.compare_digest(request.form.get("csrf", ""), session.get("csrf", "x")): abort(400)

@app.after_request
def headers(resp):
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["X-Robots-Tag"] = "noindex, nofollow"
    resp.headers["Cache-Control"] = "no-store"
    return resp

PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>MURYA messages</title>
<style>body{font-family:Arial,sans-serif;background:#f5f5f5;padding:10px;color:#14261b}.card{background:#fff;padding:15px;border-radius:12px;margin-bottom:15px}
h1{color:#0a7e07;font-size:22px}table{width:100%;border-collapse:collapse;font-size:13px}th{background:#0a7e07;color:#fff;padding:6px;text-align:left}
td{padding:6px;border-bottom:1px solid #ddd;vertical-align:top}.btn{background:#0a7e07;color:#fff;padding:8px 12px;border-radius:8px;border:none;cursor:pointer}
.del{background:#b91c1c}input[type=text]{padding:8px;width:60%;border:1px solid #888;border-radius:8px}.ok{color:#166534}.bad{color:#b91c1c}
.note{font-size:12px;color:#4a5d52}</style></head><body>
<div class="card"><h1>MURYA questions and reports · Bauchi</h1>
<p>{{ count }} report(s) · kept {{ days }} days · <a href="/export">Export CSV (no phone numbers)</a><br>
{% if sms_ready %}<span class="ok">SMS ready as {{ sender }}</span>{% else %}<span class="bad">SMS not ready: add AT_USERNAME and AT_API_KEY in the Environment page</span>{% endif %}</p>
<p class="note">These are what citizens typed. Do not treat them as verified. Never reply with names or personal details. Hooked Hausa letters in an SMS shorten how much fits in one message.</p></div>
<div class="card" style="overflow-x:auto"><table><tr><th>Time</th><th>Phone</th><th>PU</th><th>Type</th><th>Details</th><th>Status</th><th>Reply</th></tr>
{% for r in reports %}<tr><td>{{ r.created }}</td><td>{{ r.masked }}</td><td>{{ r.pu }}</td><td>{{ r.issue_type }}</td><td>{{ r.issue }}</td>
<td>{{ 'Replied ' ~ r.replied_at if r.status == 'REPLIED' else 'New' }}</td>
<td><form action="/reply" method="post"><input type="hidden" name="csrf" value="{{ csrf }}"><input type="hidden" name="id" value="{{ r.id }}">
<input type="text" name="message" maxlength="300" placeholder="Mun karbi..." required aria-label="Reply message"> <button class="btn" type="submit">Send as {{ sender }}</button></form>
<form action="/delete" method="post" style="margin-top:6px"><input type="hidden" name="csrf" value="{{ csrf }}"><input type="hidden" name="id" value="{{ r.id }}"><button class="btn del" type="submit">Delete</button></form></td></tr>
{% else %}<tr><td colspan="7">No reports yet.</td></tr>{% endfor %}</table></div></body></html>"""

RESULT = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>MURYA</title></head>
<body style="font-family:Arial,sans-serif;padding:16px"><h2>{{ title }}</h2><p>{{ body }}</p><p><a href="/dashboard">Back to the dashboard</a></p></body></html>"""

def result(title, body, code=200):
    return Response(render_template_string(RESULT, title=title, body=body), code)   # autoescaped: nothing typed can run as code

@app.route("/health")
def health(): return Response("ok", mimetype="text/plain")

@app.route("/")
@app.route("/dashboard")
@require_admin
def dashboard():
    purge_old()
    with db() as c: rows = [dict(r) for r in c.execute("SELECT * FROM reports ORDER BY id DESC LIMIT 500")]
    for r in rows: r["masked"] = mask_phone(r["phone"])
    return render_template_string(PAGE, reports=rows, count=len(rows), days=RETENTION_DAYS, sms_ready=bool(sms), sender=AT_SENDER_ID, csrf=csrf_token())

@app.route("/reply", methods=["POST"])
@require_admin
def reply_sms():
    check_csrf()
    rid, message = request.form.get("id", type=int), clean_text(request.form.get("message", ""), 300)
    with db() as c: row = c.execute("SELECT * FROM reports WHERE id=?", (rid,)).fetchone() if rid else None
    if not row or not message: return result("Nothing sent", "The report or the message was missing.", 400)
    if not sms: return result("SMS is not set up", "Add AT_USERNAME and AT_API_KEY in the Environment page, then redeploy.", 503)
    try:
        resp = sms.send(message, [row["phone"]], sender_id=AT_SENDER_ID) if AT_SENDER_ID else sms.send(message, [row["phone"]])
        rec = resp["SMSMessageData"]["Recipients"][0]
        sent = rec.get("status") == "Success"
        why = rec.get("status", "unknown")
    except Exception as e:
        sent, why = False, type(e).__name__
    if not sent: return result("Not sent", f"Africa's Talking said: {why}. Check your keys, balance and sender ID.", 502)
    with db() as c: c.execute("UPDATE reports SET status='REPLIED', replied_at=? WHERE id=?", (now(), rid))
    return result(f"Sent as {AT_SENDER_ID}", f"Reply sent to {mask_phone(row['phone'])}.")

@app.route("/delete", methods=["POST"])
@require_admin
def delete_report():
    check_csrf()
    rid = request.form.get("id", type=int)
    with db() as c: c.execute("DELETE FROM reports WHERE id=?", (rid,))
    return result("Deleted", "The report was deleted.")

@app.route("/export")
@require_admin
def export_csv():
    with db() as c: rows = c.execute("SELECT * FROM reports ORDER BY id").fetchall()
    si = io.StringIO(); cw = csv.writer(si)
    cw.writerow(["id", "time", "phone_id", "pu", "issue_type", "issue", "language", "status"])
    for r in rows: cw.writerow([r["id"], r["created"], phone_id(r["phone"]), r["pu"], r["issue_type"], r["issue"], r["lang"], r["status"]])
    return Response(si.getvalue(), mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=murya_reports.csv"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
