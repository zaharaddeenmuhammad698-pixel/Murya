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
<div class="subtitle">Muryar Zabe - Bauchi | Zaharaddeen Muhammad | AI4Elections</div>
""", unsafe_allow_html=True)

FILE = "murya_strong.csv"
if not os.path.exists(FILE):
    with open(FILE, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(["tambaya","amsa","lokaci","status"])

FAQ_4 = [
    {"q": "Ta yaya zan duba katin zabe na na dindindin?", "a": "Je zuwa shafin ofishin mai zaman kanta(inec.gov.ng) ko ka je ofishin ta mafi kusa da kai a Bauchi. Tafi da lambar shaida na mai zabe naka."},
    {"q": "Yaushe zaben 2027 zai gudana?", "a": "Zaben gama garin zai gudana ne a watan janairun 2027. Murya zata sanar da kai da zarar Hukumar zabe Mai zaman kanta ta kasa ta yi Wani sauyi. Ka guji labaran karya."},
    {"q": "Ina zan karbi katin zabe na dindindin dina a Bauchi?", "a": "A ofishin Hukumar zabe Mai zaman kanta ta kasa na karamar hukumar ka a Bauchi. Dole sai da katin dan kasa ko da katin zabe na wucen gadi."},
    {"q": "Zan iya zabe ba tare da katin zabe na dindindin dina ba?", "a": "A'a! Dole sai da katin zabe na asali. Hoton waya ko photocopy ba ya aiki a rumfar zabe."},
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

# --- FINAL: CAPITALS = ENGLISH LETTERS + HAUSA-FIRST + PUNCTUATION ---
def clean_for_voice(text):
    # Keep ? . ! , for natural pause
    text = text.replace("voters.inecnigeria.org", "shafin INEC")
    text = text.replace("www.", "").replace("https://", "").replace("http://", "")
    
    # EVERY CAPITAL PLACE = CALL AS ENGLISH LETTERS
    # PVC -> P V C (English), INEC -> I N E C (English)
    replacements = {
        "PVC": " P V C ",
        "INEC": " I N E C ",
        "VIN": " V I N ",
        "LGA": " L G A ",
    }
    # Do case-insensitive replacement but keep English call
    for k, v in replacements.items():
        text = text.replace(k, v)
        text = text.replace(k.lower(), v)
        text = text.replace(k.capitalize(), v)
    
    return text

def detect_by_text(text):
    # HAUSA-FIRST: If any Hausa word exists, it's Hausa
    t = text.lower().strip()
    t_clean = t.replace("?"," ").replace("."," ").replace("!"," ").replace(","," ").replace("'"," ")
    words = t_clean.split()
    
    hausa_dict = [
        "yaya","ina","me","mene","menene","wanene","yaushe","yau","gobe","jiya",
        "zan","zai","zaa","nan","can","su","mu","ku","ni","kai","ke","ita","shi",
        "suna","muna","kuna","yake","nake","take","don","domin","kuma","amma",
        "idan","sai","daga","zuwa","cikin","akan","ba","ne","ce","da","ko",
        "shin","eh","a'a","gaskiya","lafiya","gida","aiki","makaranta","kudi",
        "zabe","bauchi","karbi","duba","tafi","je","zo","nawa","yanzu","tukuna","kawai"
    ]
    
    ha_count = sum(1 for w in words if w in hausa_dict)
    if ha_count >= 1:
        return "ha"
    return "en"

def speak_auto(text, name):
    cleaned = clean_for_voice(text)
    lang = detect_by_text(text)
    try:
        gTTS(cleaned, lang=lang, slow=False).save(name)
        st.audio(name)
    except Exception:
        try:
            gTTS(cleaned, lang="en", slow=False).save(name)
            st.audio(name)
        except:
            st.caption("🔊 Sauti na bukatar internet kadan")

# --- TABS ---
tab_info, tab_ask, tab_admin = st.tabs(["📌 Bayanan INEC + FAQ 4", "👥 Tambaya + Sauti", "🔐 Admin Direct"])

with tab_info:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("✅ Bayanan INEC Tabbatattu")
    st.markdown("""
    **Murya tana yaki da labaran karya.**
    - ✅ INEC: Zabe 2027 yana nan
    - ✅ PVC collection zai ci gaba  
    - ✅ Zaharaddeen ne ya tabbatar
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    data = get_data()
    col1.metric("Tambayoyi", len(data))
    col2.metric("Amsoshi", len([r for r in data if len(r)>1 and r[1].strip()!=""]))
    col3.metric("Jira", len([r for r in data if len(r)<2 or r[1].strip()==""]))
    
    st.markdown("---")
    st.subheader("📌 FAQ 4 - Tun Farko")
    for i, faq in enumerate(FAQ_4):
        st.markdown(f"**Q{i+1}: {faq['q']}**")
        st.success(f"A: {faq['a']}")
        if st.button(f"🔊 Sauti", key=f"faq_{i}", use_container_width=True):
            speak_auto(faq['a'], f"faq_{i}.mp3")
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
            if st.button(f"🔊 Sauti", key=f"ans_{i}", use_container_width=True):
                speak_auto(r[1], f"ans_{i}.mp3")
            st.caption(f"🕒 {r[2] if len(r)>2 else ''} | ✅ Human-verified")
            st.markdown("---")

    st.markdown("### ✍️ Yi Sabuwar Tambaya")
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
        st.success(f"✅ YA TAFI! Tambayarka ta tafi: '{st.session_state.last_q}'")
        st.balloons()

    lang = st.radio("Harshe:", ["Hausa", "English"], horizontal=True, key="lang_choice")
    placeholder = "Yaya zan duba PVC dina a Bauchi?" if lang=="Hausa" else "Please check my PVC status in Bauchi"
    q = st.text_area("Tambayarka:", placeholder=placeholder, key="q_box")

    if st.button("🚀 Aika Tambaya", use_container_width=True, type="primary"):
        if q.strip():
            add_q(q.strip())
            st.session_state.last_q = q.strip()
            st.session_state.just_sent = True
            st.session_state.clear_flag = True
            st.rerun()
        else:
            st.warning("⚠️ Rubuta tambaya da farko")

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
            st.warning(f"Akwai {len(pending)} sabuwar tambaya tana jira")
            for idx, r in pending:
                st.markdown(f"**Tambaya #{idx+1}:** {r[0]}")
                ans = st.text_area(f"Rubuta Amsa:", key=f"adm_{idx}")
                colA, colB = st.columns(2)
                with colA:
                    if st.button(f"✅ Buga Kai Tsaye", key=f"btn_{idx}", use_container_width=True, type="primary"):
                        if ans.strip():
                            add_a(idx, ans.strip())
                            st.success("🔥 YES! Amsa ta shiga app!")
                            st.balloons()
                            st.rerun()
                with colB:
                    if ans.strip():
                        if st.button(f"🔊 Sauti", key=f"test_{idx}", use_container_width=True):
                            speak_auto(ans.strip(), f"test_{idx}.mp3")
                st.markdown("---")
    elif pw != "":
        st.error("Password kuskure!")

st.markdown("---")
st.markdown("""
<div class='footer'>
<p style='font-weight:bold; color:#006400; margin:0; font-size:18px;'>🎙️ MURYA - Muryar Zabe</p>
<p style='font-size:13px; color:#333; margin:6px 0;'>Powered by <b>Zaharaddeen Muhammad</b> | Bauchi, Nigeria</p>
<p style='font-size:12px; color:#555; margin:8px 0;'>Murya is generated for people that have language & literacy barriers — Hausa voice 🔊, simple text.</p>
<p style='font-size:11px; color:#777;'>Track: Electoral Inclusion + Information Integrity | AI4Elections 2027</p>
<p style='font-size:11px; color:#006400; margin-top:10px; font-weight:bold;'>✅ No AI Hallucination — Verified by Zaharaddeen directly</p>
</div>
""", unsafe_allow_html=True)