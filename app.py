import streamlit as st
import csv, os
from datetime import datetime
from gtts import gTTS

st.set_page_config(page_title="Murya - Bauchi Voice", layout="centered", page_icon="🎙️")

st.markdown("""
<style>
.big-title {font-size:32px; font-weight:bold; color:#006400; text-align:center;}
.subtitle {text-align:center; color:#555; font-size:13px;}
.card {background:#f0fdf4; padding:15px; border-radius:12px; border:1px solid #bbf7d0; margin:10px 0;}
.footer {text-align:center; padding:20px; background:#f0fdf4; border-radius:12px; margin-top:30px; border:1px solid #bbf7d0;}
</style>
<div class="big-title">🎙️ MURYA</div>
<div class="subtitle">Muryar Zabe - Bauchi | Zaharaddeen Muhammad</div>
""", unsafe_allow_html=True)

FILE = "murya_strong.csv"
if not os.path.exists(FILE):
    with open(FILE, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(["tambaya","amsa","lokaci","status"])

FAQ_4 = [
    {"q": "Yaya zan duba PVC dina?", "a": "Je zuwa shafin INEC ko ka je ofishin INEC na kusa da kai a Bauchi. Tafi da lambar VIN dinka."},
    {"q": "Yaushe zabe 2027 zai gudana?", "a": "INEC har yanzu ba ta fitar da ranar karshe ba. Murya zata sanar da kai da zarar INEC ta tabbatar."},
    {"q": "Ina zan karbi PVC dina a Bauchi?", "a": "A ofishin INEC na karamar hukumar ka a Bauchi. Dole sai da katin dan kasa."},
    {"q": "Zan iya zabe ba tare da PVC ba?", "a": "A'a. Dole sai da katin zabe na asali. Hoton waya ba ya aiki."},
]

def get_data():
    if not os.path.exists(FILE): return []
    with open(FILE, "r", encoding="utf-8") as f:
        rows = list(csv.reader(f))
        return rows[1:] if len(rows) > 1 else []

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

# --- AUTO DETECT BY WRITTEN TEXT ---
def clean_for_voice(text):
    text = text.replace("voters.inecnigeria.org", "shafin INEC")
    text = text.replace("PVC", " katin zabe ")
    text = text.replace("VIN", " lambar VIN ")
    text = text.replace("INEC", " INEC ")
    return text

def detect_by_text(text):
    try:
        from langdetect import detect
        lang = detect(text)
        return "ha" if lang == "ha" else "en"
    except:
        # Simple fallback: if Hausa words exist, ha else en
        t = text.lower()
        if any(x in t for x in ["yaya","ina","zan","me","yau","zabe","ba","ne","ce","don","kuma"]):
            return "ha"
        return "en"

def speak_auto(text, name):
    cleaned = clean_for_voice(text)
    lang = detect_by_text(text)
    try:
        gTTS(cleaned, lang=lang, slow=False).save(name)
        st.audio(name)
    except:
        try:
            gTTS(cleaned, lang="en").save(name)
            st.audio(name)
        except:
            st.caption("🔊 Sauti na bukatar internet")

tab_info, tab_ask, tab_admin = st.tabs(["📌 Bayanan INEC", "👥 Tambaya + Sauti", "🔐 Admin"])

with tab_info:
    col1, col2, col3 = st.columns(3)
    data = get_data()
    col1.metric("Tambayoyi", len(data))
    col2.metric("Amsoshi", len([r for r in data if len(r)>1 and r[1].strip()!=""]))
    col3.metric("Jira", len([r for r in data if len(r)<2 or r[1].strip()==""]))
    st.markdown("---")
    for i, faq in enumerate(FAQ_4):
        st.markdown(f"**Q{i+1}: {faq['q']}**")
        st.success(f"A: {faq['a']}")
        if st.button(f"🔊 Sauti", key=f"faq_{i}", use_container_width=True):
            speak_auto(faq['a'], f"faq_{i}.mp3")
        st.markdown("---")

with tab_ask:
    rows = get_data()
    answered = [r for r in rows if len(r)>1 and r[1].strip()!=""]
    for i, r in enumerate(reversed(answered)):
        st.markdown(f"**Q:** {r[0]}")
        st.success(f"**A:** {r[1]}")
        if st.button(f"🔊 Sauti", key=f"ans_{i}", use_container_width=True):
            speak_auto(r[1], f"ans_{i}.mp3")
        st.markdown("---")

    if "just_sent" not in st.session_state:
        st.session_state.just_sent = False
    if "last_q" not in st.session_state:
        st.session_state.last_q = ""
    if "clear_flag" not in st.session_state:
        st.session_state.clear_flag = False
    if st.session_state.clear_flag:
        st.session_state.q_box = ""
        st.session_state.clear_flag = False
    if st.session_state.just_sent:
        st.success(f"✅ YA TAFI! '{st.session_state.last_q}'")

    lang_choice = st.radio("Harshe:", ["Hausa", "English"], horizontal=True)
    ph = "Yaya zan duba PVC dina a Bauchi?" if lang_choice=="Hausa" else "Please check my PVC"
    q = st.text_area("Tambayarka:", placeholder=ph, key="q_box")
    if st.button("🚀 Aika Tambaya", use_container_width=True, type="primary"):
        if q.strip():
            add_q(q.strip())
            st.session_state.last_q = q.strip()
            st.session_state.just_sent = True
            st.session_state.clear_flag = True
            st.rerun()

with tab_admin:
    pw = st.text_input("Password:", type="password")
    if pw == "bauchi2027":
        rows = get_data()
        pending = [(i, r) for i, r in enumerate(rows) if len(r)<2 or r[1].strip()==""]
        for idx, r in pending:
            st.markdown(f"**{r[0]}**")
            ans = st.text_area("Amsa:", key=f"adm_{idx}")
            if st.button(f"✅ Buga", key=f"btn_{idx}", use_container_width=True):
                if ans.strip():
                    add_a(idx, ans.strip())
                    st.rerun()

st.markdown("---")
st.markdown("""
<div class='footer'>
<p style='font-weight:bold; color:#006400;'>🎙️ MURYA - Muryar Zabe</p>
<p style='font-size:13px;'>Powered by <b>Zaharaddeen Muhammad</b> | Bauchi</p>
<p style='font-size:12px;'>Murya is generated for people that have language & literacy barriers — Hausa voice, simple text.</p>
<p style='font-size:11px;'>✅ No AI Hallucination — Zaharaddeen verifies directly</p>
</div>
""", unsafe_allow_html=True)