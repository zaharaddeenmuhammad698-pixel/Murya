import streamlit as st
import csv, os
from datetime import datetime
from gtts import gTTS

st.set_page_config(page_title="Murya - Bauchi Voice", layout="centered")

st.markdown("""
<style>
.big-title {font-size:32px; font-weight:bold; color:#006400; text-align:center;}
.subtitle {text-align:center; color:#555;}
.card {background:#f0fdf4; padding:15px; border-radius:12px; border:1px solid #bbf7d0; margin:10px 0;}
</style>
<div class="big-title">🎙️ MURYA</div>
<div class="subtitle">Muryar Zabe - Bauchi | Zaharaddeen Muhammad | AI4Elections Track: Inclusion + Integrity</div>
""", unsafe_allow_html=True)

st.markdown("---")

FILE = "murya_strong.csv"
if not os.path.exists(FILE):
    with open(FILE, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(["tambaya","amsa","lokaci","status"])

FAQ_4 = [
    {"q": "Yaya zan duba PVC dina?", "a": "Je zuwa voters.inecnigeria.org ko ka je ofishin INEC na kusa da kai a Bauchi. Tafi da lambar VIN dinka."},
    {"q": "Yaushe zabe 2027 zai gudana?", "a": "INEC har yanzu ba ta fitar da ranar karshe ba. Murya zata sanar da kai da zarar INEC ta tabbatar. Ka guji labaran karya."},
    {"q": "Ina zan karbi PVC dina a Bauchi?", "a": "A ofishin INEC na karamar hukumar ka. Kowane LGA a Bauchi tana da ofishi. Dole sai da katin dan kasa."},
    {"q": "Zan iya zabe ba tare da PVC ba?", "a": "A'a. Dole sai da PVC na asali. Hoton waya ko photocopy ba ya aiki a rumfar zabe."},
]

def get_data():
    if not os.path.exists(FILE): return []
    with open(FILE, "r", encoding="utf-8") as f:
        rows = list(csv.reader(f))
        return rows[1:] if len(rows)>1 else []

def add_q(t):
    with open(FILE, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([t, "", datetime.now().strftime("%Y-%m-%d %H:%M"), "NEW"])

def add_a(idx, a):
    data = get_data()
    if 0 <= idx < len(data):
        data[idx][1] = a
        data[idx][2] = datetime.now().strftime("%Y-%m-%d %H:%M")
        data[idx][3] = "ANSWERED"
    with open(FILE, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["tambaya","amsa","lokaci","status"])
        w.writerows(data)

def speak(text, name):
    try:
        try: gTTS(text, lang="ha").save(name)
        except: gTTS(text, lang="en").save(name)
        st.audio(name)
    except:
        st.caption("🔊 Sauti na bukatar internet kadan")

tab_info, tab_ask, tab_admin = st.tabs(["📌 Bayanan INEC + FAQ 4", "👥 Tambaya + Sauti", "🔐 Admin Direct"])

with tab_info:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("✅ Bayanan INEC Tabbatattu")
    st.markdown("**Murya tana yaki da labaran karya.**\n- INEC: Zabe 2027 yana nan\n- INEC: PVC collection zai ci gaba")
    st.markdown('</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    data = get_data()
    col1.metric("Tambayoyi", len(data))
    col2.metric("Amsoshi", len([r for r in data if len(r)>1 and r[1].strip()!=""]))
    col3.metric("Jira Amsa", len([r for r in data if len(r)<2 or r[1].strip()==""]))
    st.markdown("---")
    st.subheader("📌 FAQ 4 - Tun Farko")
    for i, faq in enumerate(FAQ_4):
        st.markdown(f"**Q{i+1}: {faq['q']}**")
        st.success(f"A: {faq['a']}")
        if st.button(f"🔊 Ji Sauti FAQ {i+1}", key=f"faq_{i}"):
            speak(faq['a'], f"faq_{i}.mp3")
        st.markdown("---")

with tab_ask:
    st.subheader("👥 Amsoshin Zaharaddeen Kai Tsaye + Murya")
    rows = get_data()
    answered = [r for r in rows if len(r)>1 and r[1].strip()!=""]
    if not answered:
        st.warning("Babu amsa tukuna — Zaharaddeen zai amsa kai tsaye.")
    else:
        for i, r in enumerate(reversed(answered)):
            st.markdown(f"**Q:** {r[0]}")
            st.success(f"**A:** {r[1]}")
            if st.button(f"🔊 Sauti", key=f"v_{i}"):
                speak(r[1], f"ans_{i}.mp3")
            st.markdown("---")

    # --- FIXED TO WORK EVERY TIME ---
    st.markdown("### ✍️ Yi Sabuwar Tambaya")

    if "just_sent" not in st.session_state:
        st.session_state.just_sent = False
    if "last_q" not in st.session_state:
        st.session_state.last_q = ""
    if "q_box" not in st.session_state:
        st.session_state.q_box = ""

    # Show TA TAFI if just sent — stays but allows new typing
    if st.session_state.just_sent:
        st.success(f"✅ YA TAFI! '{st.session_state.last_q}' — Zaharaddeen zai amsa yanzu!")
        st.balloons()

    lang = st.radio("Harshe:", ["Hausa", "English"], horizontal=True, key="lang_choice")
    placeholder = "Yaya zan duba PVC dina a Bauchi?" if lang=="Hausa" else "Please those my PVC ready to collect"

    q = st.text_area("Tambayarka:", placeholder=placeholder, key="q_box")
    
    if st.button("🚀 Aika Tambaya", use_container_width=True):
        if q.strip():
            add_q(q.strip())
            st.session_state.last_q = q.strip()
            st.session_state.just_sent = True
            st.session_state.q_box = ""  # <-- THIS CLEARS THE BOX COMPLETELY
            st.rerun()
        else:
            st.warning("⚠️ Rubuta tambaya da farko")
    # --- END FIX ---

with tab_admin:
    st.subheader("🔐 Naka Kadai — Amsa Kai Tsaye")
    pw = st.text_input("Password:", type="password")
    if pw == "bauchi2027":
        st.success("Barka da zuwa, Zaharaddeen!")
        rows = get_data()
        pending = [(i, r) for i, r in enumerate(rows) if len(r)<2 or r[1].strip()==""]
        if not pending:
            st.info("Babu sabbin tambayoyi — duk an amsa!")
        else:
            for idx, r in pending:
                st.markdown(f"**Tambaya #{idx+1}:** {r[0]}")
                ans = st.text_area(f"Rubuta Amsa:", key=f"adm_{idx}")
                if st.button(f"✅ Buga Kai Tsaye + Sauti", key=f"btn_{idx}", use_container_width=True):
                    if ans.strip():
                        add_a(idx, ans.strip())
                        st.success("🔥 YES! Amsa ta shiga app kai tsaye!")
                        st.balloons()
                        st.rerun()
    elif pw != "":
        st.error("Password kuskure!")