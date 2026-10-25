import streamlit as st
import csv, os, re, io, uuid, time, html, sqlite3, hashlib, hmac
from datetime import datetime
from urllib.parse import quote
from gtts import gTTS
import pandas as pd

st.set_page_config(page_title="MURYA - INEC x Bauchi Dashboard", layout="wide", page_icon="🎙️")

st.markdown("""
<style>
header[data-testid="stHeader"], div[data-testid="stToolbar"], footer {display:none !important;}
.block-container {padding-top:0.4rem !important; max-width:1400px;}
.logo-text b {font-size:20px; color:#0a3d1a; font-weight:900;}
.logo-text span {font-size:11px; color:#0a7a2e; font-weight:600;}
.menu-box {background:white; padding:16px; border-radius:12px; border:1px solid #e0e0e0; box-shadow:0 4px 12px rgba(0,0,0,0.08); margin-bottom:12px;}
.about-hero {background:linear-gradient(135deg, #0a7a2e 0%, #1b5e20 100%); padding:22px; border-radius:16px; color:white; margin-bottom:14px;}
.about-card {background:white; padding:16px; border-radius:12px; border:1px solid #e0e0e0; box-shadow:0 1px 4px rgba(0,0,0,0.05); margin-bottom:12px;}
.section-title {font-size:13px; font-weight:800; color:#006400; border-bottom:2px solid #bbf7d0; padding-bottom:5px; margin-bottom:10px;}
.metric-card {background:white; border:1px solid #e0e0e0; padding:12px; border-radius:10px; text-align:center; box-shadow:0 1px 2px rgba(0,0,0,0.05);}
.metric-num {font-size:22px; font-weight:800; color:#006400;}
.metric-lab {font-size:10px; font-weight:700; color:#666;}
.voice-tip {background:#f1f8e9; padding:6px 8px; border-radius:6px; border-left:3px solid #66bb6a; font-size:11px; margin-bottom:8px;}
.bubble-user {background:#d9fdd3; padding:7px 10px; border-radius:12px 12px 0 12px; margin:6px 0 6px 10%; font-size:12px; box-shadow:0 1px 0.5px rgba(0,0,0,0.13);}
.bubble-admin {background:white; padding:7px 10px; border-radius:12px 12px 12px 0; margin:6px 10% 6px 0; font-size:12px; box-shadow:0 1px 0.5px rgba(0,0,0,0.13);}
.bubble-meta {font-size:9px; color:#667781; text-align:right; margin-top:2px;}
.admin-on {background:#1b5e20; color:white; padding:4px 10px; border-radius:20px; font-size:11px; font-weight:700;}
</style>
""", unsafe_allow_html=True)

# ======================= SECURITY =======================
# Salted PBKDF2-SHA256 hash of the admin password (the password itself is NOT stored here).
PW_SALT = bytes.fromhex("aff5e5545c0ecd043e7e48ea3759e374")
PW_HASH = "528dec6f356d63251ca16eabac6d994e5b7c2cd2221b14c971ff376d05d121b2"
PW_ITER = 200_000

def verify_pw(pw: str) -> bool:
    h = hashlib.pbkdf2_hmac("sha256", pw.encode("utf-8"), PW_SALT, PW_ITER).hex()
    return hmac.compare_digest(h, PW_HASH)

def esc(text) -> str:
    """Escape user text for safe HTML display, keep line breaks."""
    return html.escape(str(text)).replace("\n", "<br>")

def login(key: str):
    """Callback for password inputs. Locks for 5 min after 5 wrong tries."""
    ss = st.session_state
    if ss.lock_until > time.time():
        ss.login_msg = "locked"; ss[key] = ""; return
    pw = ss.get(key, "")
    ss[key] = ""
    if not pw: return
    if verify_pw(pw):
        ss.is_admin = True; ss.fails = 0; ss.login_msg = "ok"
    else:
        ss.fails += 1; ss.login_msg = "bad"
        if ss.fails >= 5:
            ss.lock_until = time.time() + 300; ss.fails = 0

def logout():
    st.session_state.is_admin = False; st.session_state.login_msg = ""

def login_feedback():
    m = st.session_state.login_msg
    if m == "bad": st.error("Password kuskure!")
    elif m == "locked": st.error("An kulle na minti 5 saboda yunƙuri da yawa.")

# ======================= DATABASE (SQLite) =======================
DB = "murya.db"
OLD_CSV = "murya_strong.csv"
os.makedirs("voice_notes/incoming", exist_ok=True)
os.makedirs("voice_notes/replies", exist_ok=True)

def _conn():
    c = sqlite3.connect(DB, timeout=10)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL")
    return c

def init_db():
    with _conn() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS questions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            q TEXT NOT NULL, a TEXT DEFAULT '', created TEXT,
            status TEXT DEFAULT 'NEW', sid TEXT DEFAULT '')""")
        if os.path.exists(OLD_CSV) and c.execute("SELECT COUNT(*) FROM questions").fetchone()[0] == 0:
            try:
                with open(OLD_CSV, encoding="utf-8") as f:
                    rows = list(csv.reader(f))[1:]
                for r in rows:
                    if r and r[0].strip():
                        a = r[1] if len(r) > 1 else ""
                        c.execute("INSERT INTO questions(q,a,created,status) VALUES(?,?,?,?)",
                                  (r[0], a, r[2] if len(r) > 2 else "", "ANSWERED" if a.strip() else "NEW"))
            except Exception:
                pass
init_db()

def get_data():
    with _conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM questions ORDER BY id")]

def add_q(text, sid=""):
    text = text.strip()[:500]
    if not text: return
    with _conn() as c:
        c.execute("INSERT INTO questions(q,created,sid) VALUES(?,?,?)",
                  (text, datetime.now().strftime("%Y-%m-%d %H:%M"), sid))

def add_a(qid, a):
    with _conn() as c:
        c.execute("UPDATE questions SET a=?, status='ANSWERED' WHERE id=?", (a.strip()[:1000], qid))

def delete_q(qid):
    with _conn() as c:
        c.execute("DELETE FROM questions WHERE id=?", (qid,))

# ======================= VOICE / LANGUAGE =======================
def clean_for_voice(text):
    text = text.replace("voters.inecnigeria.org", "shafin INEC").replace("www.", "").replace("https://", "").replace("http://", "")
    for k, v in {"PVC": " P V C ", "INEC": " I N E C ", "VIN": " V I N ", "LGA": " L G A ", "PU": " P U "}.items():
        text = re.sub(rf"\b{k}\b", v, text, flags=re.IGNORECASE)
    return text

# Only Hausa-specific words (words shared with English like me/da/ba/ko/can/su were removed)
HAUSA_WORDS = {"yaya","ina","mene","menene","wanene","yaushe","yau","gobe","jiya","zan","zai","zaa","suna","muna",
    "kuna","yake","nake","take","domin","kuma","amma","idan","daga","zuwa","cikin","akan","shin","gaskiya","lafiya",
    "gida","aiki","makaranta","kudi","zabe","zaben","karbi","duba","tafi","nawa","yanzu","tukuna","kawai","tambaya",
    "amsa","katin","katina","dindindin","kasa","ofishin","hukumar","wannan","akwai","babu","yadda","dina"}

def detect_by_text(text):
    words = re.findall(r"[a-zA-Z']+", text.lower())
    if not words: return "en"
    hits = sum(1 for w in words if w in HAUSA_WORDS)
    return "ha" if hits >= 2 or hits / len(words) >= 0.3 else "en"

@st.cache_data(show_spinner=False, max_entries=200)
def tts_bytes(text, lang):
    buf = io.BytesIO()
    gTTS(clean_for_voice(text), lang=lang, slow=False).write_to_fp(buf)
    return buf.getvalue()

def speak_auto(text):
    for lang in dict.fromkeys([detect_by_text(text), "en"]):
        try:
            st.audio(tts_bytes(text, lang), format="audio/mp3"); return
        except Exception:
            continue
    st.caption("🔊 Sauti na bukatar internet kadan")

def wa_link(text):
    return "https://wa.me/?text=" + quote("Murya Bauchi - " + text[:400])

# ======================= SESSION STATE =======================
defaults = {"menu_open": False, "page": "About Us", "voice_key": 0, "just_sent": False, "last_q": "",
            "voice_sent": False, "last_voice": "", "is_admin": False, "fails": 0, "lock_until": 0.0,
            "login_msg": "", "sid": uuid.uuid4().hex[:8]}
for k, v in defaults.items():
    if k not in st.session_state: st.session_state[k] = v
IS_ADMIN = st.session_state.is_admin
SID = st.session_state.sid

# NOTE: verify this date against the official INEC timetable before the demo.
FAQ_4 = [
    {"q": "Ta yaya zan duba katin zabe na na dindindin?", "a": "Je zuwa shafin Hukumar Zabe Mai Zaman Kanta (inec.gov.ng) ko ka je ofishinta mafi kusa da kai a Bauchi."},
    {"q": "Yaushe zaben 2027 zai gudana?", "a": "Zaben gama gari zai gudana ne a watan Janairun 2027. Murya za ta sanar da kai da zarar Hukumar Zabe Mai Zaman Kanta ta yi wani sauyi."},
    {"q": "Ina zan karbi katin zabe na dindindin a Bauchi?", "a": "A ofishin Hukumar Zabe Mai Zaman Kanta na karamar hukumar ka a Bauchi."},
    {"q": "Zan iya zabe ba tare da katin zabe na dindindin ba?", "a": "A'a! Dole sai da katin zabe na asali. Hoton waya ko photocopy ba ya aiki."},
]

def go(page):
    st.session_state.page = page

# ======================= TOP NAV =======================
c1, c2 = st.columns([5, 1])
with c1:
    st.markdown('<div class="logo-text"><b>✓ INEC | 🎙️ MURYA</b><br><span>Muryar Zabe - Bauchi | Civic Tech • Citizen Voices • Transparent Elections</span></div>', unsafe_allow_html=True)
with c2:
    if st.button("☰", key="ham", use_container_width=True):
        st.session_state.menu_open = not st.session_state.menu_open

if st.session_state.menu_open:
    st.markdown('<div class="menu-box"><b>Menu</b></div>', unsafe_allow_html=True)
    items = ["About Us", "Dashboard", "Bayanan INEC", "Chat (Text + Murya)", "Charts & Analytics", "Admin Login", "Contact"]
    cols = st.columns(2)
    for i, it in enumerate(items):
        with cols[i % 2]:
            if st.button(f"{'✅ ' if st.session_state.page == it else ''}{it}", key=f"m_{it}", use_container_width=True,
                         type="primary" if st.session_state.page == it else "secondary"):
                st.session_state.page = it; st.session_state.menu_open = False; st.rerun()

page = st.session_state.page

# ======================= ABOUT US =======================
if page == "About Us":
    st.markdown("""
    <div class="about-hero">
    <h2 style="margin:0; color:white;">🎙️ MURYA - Muryar Zabe</h2>
    <p style="margin:8px 0 0 0; font-size:14px; line-height:1.6; color:#e8f5e9;">
    The first voice-based civic tech platform for Bauchi — breaking language & literacy barriers for 2027 elections.<br>
    <b>Track:</b> Electoral Inclusion + Information Integrity | AI4Elections Hackathon 2027 | Bauchi, Nigeria
    </p></div>
    """, unsafe_allow_html=True)
    a, b = st.columns([2, 1])
    with a:
        st.markdown("""
        <div class="about-card">
        <div class="section-title">🎯 The Problem</div>
        <p style="font-size:13px; line-height:1.6;">
        In Bauchi, many voters struggle with English-language INEC information. Many cannot read or write but speak Hausa fluently.
        Fake news about PVC & election dates spreads faster than official info. Result: voter apathy & exclusion — especially women, elderly, rural.
        </p>
        <div class="section-title">💡 Our Solution: MURYA</div>
        <p style="font-size:13px; line-height:1.6;">
        <b>Murya (Voice)</b> allows citizens to:<br>
        • Ask in Hausa by <b>text or voice</b> like WhatsApp — press mic<br>
        • Get <b>human-verified INEC answers</b> — no AI hallucination<br>
        • <b>Listen 🔊</b> — text-to-speech for those who cannot read<br>
        • <b>Share verified info</b> — one-click WhatsApp share to fight fake news<br><br>
        <b>Innovation:</b> Unified text+voice timeline and 100% human verification.
        </p>
        <div class="section-title">🛠️ How It Works</div>
        <p style="font-size:12px;">1️⃣ Ask (Rubuta ko yi murya) → 2️⃣ Verify (Zaharaddeen checks INEC) → 3️⃣ Answer (Chat + Voice + Share)</p>
        </div>
        """, unsafe_allow_html=True)
    with b:
        st.markdown("""
        <div class="about-card">
        <div class="section-title">📊 Why Bauchi</div>
        <p style="font-size:12px;">• 20 LGAs<br>• High Hausa-speaking population<br>• Low digital literacy<br>• High fake news risk in 2027<br><br>Built <b>by Bauchi, for Bauchi</b>.</p>
        <div class="section-title">👤 Team</div>
        <p style="font-size:13px; font-weight:700; color:#006400;">Zaharaddeen Muhammad</p>
        <p style="font-size:11px; color:#555;">Civic Tech Builder | Bauchi</p>
        <div style="background:#e8f5e9; padding:8px; border-radius:8px; font-size:11px;">✅ No AI Hallucination — Verified by Zaharaddeen directly from INEC portal.</div>
        </div>
        """, unsafe_allow_html=True)
        st.button("🚀 Open Dashboard →", use_container_width=True, type="primary", on_click=go, args=("Dashboard",))
        st.button("Admin Login", use_container_width=True, on_click=go, args=("Admin Login",))
        st.button("Ask a Question", use_container_width=True, on_click=go, args=("Chat (Text + Murya)",))

# ======================= DASHBOARD =======================
elif page == "Dashboard":
    data = get_data()
    ans = len([r for r in data if r["a"].strip()])
    pen = len(data) - ans
    vc = len([f for f in os.listdir("voice_notes/incoming") if f.endswith(".wav")])
    st.markdown("### 📊 Dashboard")
    m1, m2, m3, m4 = st.columns(4)
    for col, num, lab in [(m1, len(data), "TAMBAYOYI"), (m2, ans, "AMSOSHI"), (m3, pen, "JIRA"), (m4, vc, "MURYOYI")]:
        with col: st.markdown(f'<div class="metric-card"><div class="metric-num">{num}</div><div class="metric-lab">{lab}</div></div>', unsafe_allow_html=True)
    if IS_ADMIN: st.markdown('<div style="margin:8px 0;"><span class="admin-on">🔐 ADMIN MODE ON</span></div>', unsafe_allow_html=True)

    left, mid, right = st.columns([1.1, 1.6, 0.9])
    with left:
        st.markdown('<div class="about-card"><div class="section-title">✅ Bayanan INEC Preview</div>INEC: Zabe 2027 yana nan, PVC collection zai ci gaba. Zaharaddeen ne ya tabbatar — yaki da labaran karya.</div>', unsafe_allow_html=True)
        for i, f in enumerate(FAQ_4):
            st.markdown(f'<div class="about-card"><b>Q{i+1}: {esc(f["q"])}</b><br><span style="color:#006400;">A: {esc(f["a"])}</span></div>', unsafe_allow_html=True)
    with mid:
        st.markdown('<div class="about-card"><div class="section-title">💬 Verified Answers</div>', unsafe_allow_html=True)
        st.markdown('<div class="voice-tip"><b>🎤 Ga wanda bai iya rubutu ba</b> — kamar WhatsApp.</div>', unsafe_allow_html=True)
        answered = [r for r in data if r["a"].strip()][-5:]
        if not answered: st.caption("Babu amsoshi tukuna.")
        for r in answered:
            st.markdown(f'<div class="bubble-user">{esc(r["q"])}</div><div class="bubble-admin"><b>Zaharaddeen:</b> {esc(r["a"])}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.button("Go to Full Chat →", use_container_width=True, on_click=go, args=("Chat (Text + Murya)",))
    with right:
        st.markdown('<div class="about-card"><div class="section-title">🔐 Admin</div>', unsafe_allow_html=True)
        if IS_ADMIN:
            st.success("ADMIN ON — Go to Chat to delete spam")
            st.button("Logout", key="logout_dash", on_click=logout)
        else:
            st.text_input("Password:", type="password", key="pw_dash", on_change=login, args=("pw_dash",))
            login_feedback()
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="about-card"><div class="section-title">📈 Charts Preview</div>', unsafe_allow_html=True)
        if data: st.bar_chart(pd.DataFrame({"Amsoshi": [ans], "Jira": [pen]}).T)
        st.markdown('</div>', unsafe_allow_html=True)

# ======================= BAYANAN INEC =======================
elif page == "Bayanan INEC":
    st.markdown("### 📌 Bayanan INEC + FAQ 4 (Tabbatattu)")
    for i, faq in enumerate(FAQ_4):
        st.markdown(f'<div class="about-card"><b>Q{i+1}: {esc(faq["q"])}</b><br><span style="color:#006400;">A: {esc(faq["a"])}</span></div>', unsafe_allow_html=True)
        if st.button(f"🔊 Sauti Q{i+1}", key=f"faq_{i}"): speak_auto(faq["a"])

# ======================= CHARTS =======================
elif page == "Charts & Analytics":
    st.markdown("### 📈 Charts & Analytics")
    data = get_data()
    if not data: st.info("Babu data tukuna — tambayoyi zasu bayyana a charts anan")
    else:
        ans = len([r for r in data if r["a"].strip()]); pen = len(data) - ans
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="about-card"><div class="section-title">Status</div>', unsafe_allow_html=True)
            st.bar_chart(pd.DataFrame({"Amsoshi": [ans], "Jira": [pen]}))
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="about-card"><div class="section-title">Growth</div>', unsafe_allow_html=True)
            st.line_chart(pd.DataFrame({"Tambayoyi": list(range(1, len(data) + 1))}))
            st.markdown('</div>', unsafe_allow_html=True)

# ======================= CHAT =======================
elif page.startswith("Chat"):
    st.markdown("### 💬 Chat — Text + Murya (Kamar WhatsApp)")
    st.markdown('<div class="voice-tip"><b>🎤 Ga wanda bai iya rubutu ba</b> — matsa mic ka yi magana kamar WhatsApp.</div>', unsafe_allow_html=True)
    if not IS_ADMIN:
        st.caption("🔒 Tambayoyinka da muryoyinka naka ne kawai a wannan shafin.")

    if st.session_state.just_sent:
        st.success(f"✅ YA TAFI! '{st.session_state.last_q}'"); st.balloons(); st.session_state.just_sent = False
    if st.session_state.voice_sent:
        st.success(f"✅ MUN KARBA MURYARKA! {st.session_state.last_voice}"); st.balloons(); st.session_state.voice_sent = False

    def send_text():
        q = st.session_state.q_box.strip()
        if q:
            add_q(q, SID); st.session_state.last_q = q[:500]; st.session_state.just_sent = True
            st.session_state.q_box = ""

    ct, cv = st.columns([2, 1])
    with ct:
        lang = st.radio("Harshe:", ["Hausa", "English"], horizontal=True, key="lang_choice")
        placeholder = "Yaya zan duba PVC dina a Bauchi?" if lang == "Hausa" else "Please check my PVC status in Bauchi"
        st.text_area("Tambayarka:", placeholder=placeholder, key="q_box", height=70, label_visibility="collapsed", max_chars=500)
        st.button("🚀 Aika Tambaya", use_container_width=True, type="primary", on_click=send_text)
    with cv:
        st.caption("🎤 Murya:")
        voice_data = st.audio_input("Yi murya", key=f"murya_{st.session_state.voice_key}", label_visibility="collapsed")
        if voice_data is not None:
            if len(voice_data.getbuffer()) > 10 * 1024 * 1024:
                st.error("Muryar ta yi yawa - kasa da 10MB")
            else:
                ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                fname = f"Murya_{ts}_{SID}.wav"
                with open(f"voice_notes/incoming/{fname}", "wb") as f: f.write(voice_data.getbuffer())
                st.session_state.last_voice = fname; st.session_state.voice_sent = True
                st.session_state.voice_key += 1; st.rerun()

    # Build timeline (admins see all; visitors see only their own)
    chat_items = []
    for r in get_data():
        if not IS_ADMIN and r["sid"] != SID: continue
        try: t = datetime.strptime(r["created"], "%Y-%m-%d %H:%M")
        except Exception: t = datetime.min
        chat_items.append({"kind": "text", "time": t, **r})
    for fname in os.listdir("voice_notes/incoming"):
        if not fname.endswith(".wav"): continue
        if not IS_ADMIN and SID not in fname: continue
        m = re.search(r"(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})", fname)
        try: t = datetime.strptime(m.group(1), "%Y-%m-%d_%H-%M-%S") if m else datetime.min
        except Exception: t = datetime.min
        chat_items.append({"kind": "voice", "time": t, "fname": fname,
                           "incoming": f"voice_notes/incoming/{fname}", "reply": f"voice_notes/replies/{fname}"})
    chat_items.sort(key=lambda x: x["time"])

    box = st.container(height=560, border=True)
    with box:
        if not chat_items:
            st.caption("Babu sakonni tukuna — ka fara tambaya a sama.")
        for item in chat_items[-40:]:
            if item["kind"] == "text":
                st.markdown(f'<div class="bubble-user"><div style="font-weight:600; font-size:10px;">Kai:</div>{esc(item["q"])}<div class="bubble-meta">{esc(item["created"])} ✓✓</div></div>', unsafe_allow_html=True)
                share_text = f"Q: {item['q']}" + (f" | A: {item['a']}" if item["a"].strip() else "")
                c1, c2, c3 = st.columns(3)
                with c1: st.link_button("🔗 Share", wa_link(share_text))
                with c2:
                    if st.button("🔊 Sauti", key=f"sp_{item['id']}"): speak_auto(item["q"])
                if IS_ADMIN:
                    with c3:
                        if st.button("🗑️ Delete", key=f"del_{item['id']}", help="Admin only - delete spam"):
                            delete_q(item["id"]); st.toast("An goge!"); st.rerun()
                if item["a"].strip():
                    st.markdown(f'<div class="bubble-admin"><b>Zaharaddeen:</b> {esc(item["a"])}<div class="bubble-meta">{esc(item["created"])}</div></div>', unsafe_allow_html=True)
                    if st.button("🔊 Amsa", key=f"spa_{item['id']}", use_container_width=True): speak_auto(item["a"])
            else:
                if not os.path.exists(item["incoming"]): continue
                st.markdown(f'<div class="bubble-user">🎤 Sakon Murya<div class="bubble-meta">{esc(item["fname"])} ✓✓</div></div>', unsafe_allow_html=True)
                st.audio(item["incoming"])
                cv1, cv2 = st.columns(2)
                with cv1: st.link_button("🔗 Share", wa_link("Sakon Murya - Verified"))
                if IS_ADMIN:
                    with cv2:
                        if st.button("🗑️ Goge Murya", key=f"delv_{item['fname']}"):
                            for p in (item["incoming"], item["reply"]):
                                if os.path.exists(p): os.remove(p)
                            st.toast("An goge muryar!"); st.rerun()
                if os.path.exists(item["reply"]):
                    st.markdown('<div class="bubble-admin">🎙️ Amsar Murya</div>', unsafe_allow_html=True)
                    st.audio(item["reply"])

# ======================= ADMIN LOGIN =======================
elif page == "Admin Login":
    st.markdown("### 🔐 Admin Login")
    if not IS_ADMIN:
        st.text_input("Password:", type="password", key="pw_admin", on_change=login, args=("pw_admin",))
        login_feedback()
    else:
        st.success("✅ ADMIN ON — Yanzu zaka iya amsa tambayoyi da goge spam")
        st.button("Logout", key="logout_admin", on_click=logout)
        rows = get_data()
        pending = [r for r in rows if not r["a"].strip()]
        if not pending: st.info("Babu sabbin tambayoyi — duk an amsa!")
        else:
            st.warning(f"{len(pending)} sabuwar tambaya tana jira")
            for r in pending[:10]:
                col1, col2 = st.columns([4, 1])
                with col1: st.markdown(f"**#{r['id']}: {esc(r['q'][:200])}** — {esc(r['created'])}", unsafe_allow_html=True)
                with col2:
                    with st.popover("⋮"):
                        if st.button("🗑️ Delete", key=f"delA_{r['id']}", use_container_width=True):
                            delete_q(r["id"]); st.toast("An goge!"); st.rerun()
                ans_text = st.text_area("Amsa:", key=f"adm_{r['id']}", height=70, placeholder="Rubuta amsa...")
                if st.button("✅ Buga Kai Tsaye", key=f"btn_{r['id']}", type="primary", use_container_width=True):
                    if ans_text.strip(): add_a(r["id"], ans_text); st.balloons(); st.rerun()
                st.markdown("---")
        st.subheader("🎧 Muryoyi - Amsa da Murya")
        for f in sorted(os.listdir("voice_notes/incoming"), reverse=True)[:10]:
            ipath, rpath = f"voice_notes/incoming/{f}", f"voice_notes/replies/{f}"
            if not os.path.exists(ipath): continue
            st.write(f"📩 {f}"); st.audio(ipath)
            if os.path.exists(rpath): st.audio(rpath)
            rv = st.audio_input("🎤 Amsa da murya", key=f"reply_{f}")
            if rv is not None:
                with open(rpath, "wb") as out: out.write(rv.getbuffer())
                st.success("✅ Amsa ta tafi!")

# ======================= CONTACT =======================
elif page == "Contact":
    st.markdown("""
    <div class="about-card">
    <div class="section-title">📞 Contact Us</div>
    <p style="font-size:13px;">
    <b>MURYA - Muryar Zabe Bauchi</b><br>
    Civic Tech Platform • Citizen Voices • Transparent Elections<br><br>
    <b>Powered by Zaharaddeen Muhammad</b><br>Bauchi, Nigeria<br><br>
    <b>Track:</b> Electoral Inclusion + Information Integrity<br>
    <b>AI4Elections Hackathon 2027</b><br><br>
    ✅ No AI Hallucination — Every answer verified by a human directly from the INEC portal.<br><br>
    <b>How to reach us:</b> Use the Chat page to ask questions — we reply directly.
    </p></div>
    """, unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center; padding:12px; background:#f0fdf4; border-radius:10px; border:1px solid #bbf7d0; margin-top:16px;">
<p style="font-weight:bold; color:#006400; margin:0;">🎙️ MURYA - Muryar Zabe</p>
<p style="font-size:11px; color:#111; margin:2px 0;"><b>Powered by Zaharaddeen Muhammad | Bauchi, Nigeria | INEC x MURYA</b></p>
</div>
""", unsafe_allow_html=True)