import streamlit as st
import csv, os
from datetime import datetime
from gtts import gTTS

st.set_page_config(page_title="Murya - Bauchi Voice", layout="centered", page_icon="🎙️")

# --- STYLES ---
st.markdown("""
<style>
.big-title {font-size:32px; font-weight:bold; color:#006400; text-align:center;}
.subtitle {text-align:center; color:#555; font-size:13px;}
.card {background:#f0fdf4; padding:15px; border-radius:12px; border:1px solid #bbf7d0; margin:10px 0;}
.footer {text-align:center; padding:20px; background:#f0fdf4; border-radius:12px; margin-top:30px; border:1px solid #bbf7d0;}
</style>
<div class="big-title">🎙️ MURYA</div>
<div class="subtitle">Muryar Zabe - Bauchi | Zaharaddeen Muhammad | AI4Elections Track: Inclusion + Integrity</div>
""", unsafe_allow_html=True)

st.markdown("---")

FILE = "murya_strong.csv"
if not os.path.exists(FILE):
    with open(FILE, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(["tambaya","amsa","lokaci","status"])

# --- FAQ 4 - ALWAYS THERE ---
FAQ_4 = [
    {"q": "Yaya zan duba PVC dina?", "a": "Je zuwa shafin INEC ko ka je ofishin INEC na kusa da kai a Bauchi. Tafi da lambar V I N dinka."},
    {"q": "Yaushe zabe 2027 zai gudana?", "a": "I N E C har yanzu ba ta fitar da ranar karshe ba. Murya zata sanar da kai da zarar I N E C ta tabbatar. Ka guji labaran karya."},
    {"q": "Ina zan karbi PVC dina a Bauchi?", "a": "A ofishin I N E C na karamar hukumar ka. Kowane LGA a Bauchi tana da ofishi. Dole sai da katin dan kasa."},
    {"q": "Zan iya zabe ba tare da PVC ba?", "a": "A'a. Dole sai da katin zabe P V C na asali. Hoton waya ko photocopy ba ya aiki a rumfar zabe."},
]

# --- DATA FUNCTIONS ---
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

# --- PROFESSIONAL VOICE FIX (No more Hausa + English mixing) ---
def clean_for_voice(text):
    text = text.replace("voters.inecnigeria.org", "shafin I N E C")
    text = text.replace("www.", "").replace("https://", "").replace("http://", "")
    text = text.replace("PVC", " katin zabe ")
    text = text.replace("VIN", " lambar V I N ")
    text = text.replace("INEC", " I N E C ")
    text = text.replace("LGA", " karamar hukuma ")
    return text

def speak(text, name, lang_choice="ha"):
    try:
        cleaned = clean_for_voice(text)
        if lang_choice == "ha":
            gTTS(cleaned, lang="ha", slow=False).save(name)
        else:
            gTTS(cleaned, lang="en", slow=False).save(name)
        st.audio(name)
    except Exception:
        try:
            gTTS(text, lang="en").save(name)
            st.audio(name)
        except:
            st.caption("🔊 Sauti na bukatar internet kadan — rubutu yana nan.")

# --- TABS ---
tab_info, tab_ask, tab_admin = st.tabs(["📌 Bayanan INEC + FAQ 4", "👥 Tambaya + Sauti", "🔐 Admin Direct"])

with tab_info:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("✅ Bayanan INEC Tabbatattu (Human-verified)")
    st.markdown("""
    **Murya tana yaki da labaran karya.**
    - ✅ INEC: Zabe 2027 yana nan, ba a canza ba.
    - ✅ INEC: PVC collection zai ci gaba.
    - ✅ Duk amsa a Murya Zaharaddeen ne ya tabbatar da ita da kansa — ba AI hallucination ba.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    data = get_data()
    col1.metric("Tambayoyi", len(data))
    col2.metric("Amsoshi", len([r for r in data if len(r)>1 and r[1].strip()!=""]))
    col3.metric("Jira Amsa", len([r for r in data if len(r)<2 or r[1].strip()==""]))
    
    st.markdown("---")
    st.subheader("📌 FAQ 4 - Tun Farko (Always There)")
    st.caption("Wadannan 4 tambayoyi ne muka sanya tun farko — suna nan koyaushe.")
    for i, faq in enumerate(FAQ_4):
        st.markdown(f"**Q{i+1}: {faq['q']}**")
        st.success(f"A: {faq['a']}")
        c1, c2 = st.columns(2)
        with c1:
            if st.button(f"🔊 Hausa", key=f"faq_ha_{i}", use_container_width=True):
                speak(faq['a'], f"faq_ha_{i}.mp3", "ha")
        with c2:
            if st.button(f"🔊 English", key=f"faq_en_{i}", use_container_width=True):
                speak(faq['a'], f"faq_en_{i}.mp3", "en")
        st.markdown("---")
    
    st.info("🎯 Track: Electoral Inclusion (Hausa Voice, low-literacy) + Information Integrity (Human-in-loop)")

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
            c1, c2 = st.columns(2)
            with c1:
                if st.button(f"🔊 Hausa", key=f"ans_ha_{i}", use_container_width=True):
                    speak(r[1], f"ans_ha_{i}.mp3", "ha")
            with c2:
                if st.button(f"🔊 English", key=f"ans_en_{i}", use_container_width=True):
                    speak(r[1], f"ans_en_{i}.mp3", "en")
            st.caption(f"🕒 {r[2] if len(r)>2 else ''} | ✅ Human-verified")
            st.markdown("---")

    # --- BUG FIX: WORKS EVERY TIME + CLEARS BOX ---
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
        st.caption("Zaharaddeen zai amsa ta — amsa zata bayyana a sama da murya.")
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
    st.subheader("🔐 Naka Kadai — Amsa Kai Tsaye Zuwa App")
    st.caption("Wannan shine abin da kake nema: reply goes directly into app + voice")
    pw = st.text_input("Password:", type="password")
    if pw == "bauchi2027":
        st.success("Barka da zuwa, Zaharaddeen! Kai ne zaka amsa kai tsaye.")
        rows = get_data()
        pending = [(i, r) for i, r in enumerate(rows) if len(r)<2 or r[1].strip()==""]
        if not pending:
            st.info("Babu sabbin tambayoyi — duk an amsa!")
            if rows:
                st.write("Tambayoyi 5 na karshe:")
                for r in rows[-5:]:
                    st.text(f"Q: {r[0]} -> A: {r[1][:50]}")
        else:
            st.warning(f"Akwai {len(pending)} sabuwar tambaya tana jira ka")
            for idx, r in pending:
                st.markdown(f"**Tambaya #{idx+1}:** {r[0]}")
                st.caption(f"Lokaci: {r[2] if len(r)>2 else ''}")
                ans = st.text_area(f"Rubuta Amsa kai tsaye:", key=f"adm_{idx}", placeholder="Amsarka a nan...")
                colA, colB = st.columns(2)
                with colA:
                    if st.button(f"✅ Buga Kai Tsaye + Sauti", key=f"btn_{idx}", use_container_width=True, type="primary"):
                        if ans.strip():
                            add_a(idx, ans.strip())
                            st.success(f"🔥 YES! Amsa ta shiga app kai tsaye! Jama'a na iya jin ta da murya yanzu!")
                            st.balloons()
                            st.rerun()
                with colB:
                    if ans.strip():
                        if st.button(f"🔊 Gwada Sauti", key=f"test_{idx}", use_container_width=True):
                            speak(ans.strip(), f"test_{idx}.mp3", "ha")
                st.markdown("---")
    elif pw != "":
        st.error("Password kuskure! Saka: bauchi2027")

# --- FOOTER (Professional) ---
st.markdown("---")
st.markdown("""
<div class='footer'>
<p style='font-weight:bold; color:#006400; margin:0; font-size:18px;'>🎙️ MURYA - Muryar Zabe</p>
<p style='font-size:13px; color:#333; margin:6px 0;'>Powered by <b>Zaharaddeen Muhammad</b> | Bauchi, Nigeria</p>
<p style='font-size:12px; color:#555; margin:8px 0; line-height:1.5;'>
Murya is generated for people that have language & literacy barriers — Hausa voice 🔊, simple text, no big grammar.<br>
An yi ta ne domin masu matsalar harshe da karatu a Bauchi — Hausa murya, saukin rubutu, babu turanci mai yawa.
</p>
<p style='font-size:11px; color:#777; margin:5px 0;'>Track: Electoral Inclusion + Information Integrity | AI4Elections 2027 | #MuryaForBauchi</p>
<p style='font-size:11px; color:#006400; margin-top:10px; font-weight:bold;'>✅ No AI Hallucination — All answers verified by Zaharaddeen directly</p>
</div>
""", unsafe_allow_html=True)