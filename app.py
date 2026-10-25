import streamlit as st
from gtts import gTTS
import base64

st.set_page_config(page_title="Murya - Tambayoyi kan import streamlit as st
import csv, os
from datetime import datetime
from gtts import gTTS

st.set_page_config(page_title="Murya - Bauchi Voice", page_icon="🎙️", layout="centered")

# --- STRONG UI ---
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
    with open(FILE, "w", newline='', encoding='utf-8') as f:
        csv.writer(f).writerow(["tambaya","amsa","lokaci","status"])

def get_data():
    if not os.path.exists(FILE): return []
    with open(FILE, "r", encoding='utf-8') as f:
        return list(csv.reader(f))[1:]

def add_q(t):
    with open(FILE, "a", newline='', encoding='utf-8') as f:
        csv.writer(f).writerow([t, "", datetime.now().strftime("%Y-%m-%d %H:%M"), "NEW"])

def add_a(idx, a):
    data = get_data()
    if 0 <= idx < len(data):
        data[idx][1] = a
        data[idx][2] = datetime.now().strftime("%Y-%m-%d %H:%M")
        data[idx][3] = "ANSWERED"
    with open(FILE, "w", newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(["tambaya","amsa","lokaci","status"])
        w.writerows(data)

def speak(text, name):
    try:
        try:
            gTTS(text, lang='ha').save(name)
        except:
            gTTS(text, lang='en').save(name)
        st.audio(name)
    except:
        st.caption("🔊 Sauti na bukatar internet kadan — amma amsa a rubuce tana nan.")

# --- TABS - STRONG APP ---
tab_info, tab_ask, tab_admin = st.tabs(["📌 Bayanan INEC", "👥 Tambaya + Sauti", "🔐 Admin Direct"])

with tab_info:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("✅ Bayanan INEC Tabbatattu (Human-verified)")
    st.markdown("""
    **Murya tana yaki da labaran karya.**
    - INEC: Zabe 2027 yana nan, ba a canza ba.
    - INEC: PVC collection zai ci gaba.
    - Duk amsa a Murya Zaharaddeen ne ya tabbatar da ita da kansa — ba AI hallucination ba.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    data = get_data()
    col1.metric("Tambayoyi", len(data))
    col2.metric("Amsoshi", len([r for r in data if len(r)>1 and r[1].strip()!=""]))
    col3.metric("Jira Amsa", len([r for r in data if len(r)<2 or r[1].strip()==""]))
    
    st.info("🎯 Track: Electoral Inclusion (Hausa Voice, low-literacy) + Information Integrity (Human-in-loop)")

with tab_ask:
    st.subheader("Amsoshin Zaharaddeen Kai Tsaye + Murya")
    rows = get_data()
    answered = [r for r in rows if len(r)>1 and r[1].strip()!=""]
    if not answered:
        st.warning("Babu amsa tukuna — Zaharaddeen zai amsa kai tsaye.")
    else:
        for i, r in enumerate(reversed(answered)):
            st.markdown(f"**Q:** {r[0]}")
            st.success(f"**A:** {r[1]}")
            c1, c2 = st.columns([1,2])
            with c1:
                if st.button(f"🔊 Sauti", key=f"v_{i}_{r[2]}"):
                    speak(r[1], f"ans_{i}.mp3")
            with c2:
                st.caption(f"🕒 {r[2]} | Status: {r[3] if len(r)>3 else 'ANSWERED'}")
            st.markdown("---")

    st.markdown("### ✍️ Yi Sabuwar Tambaya")
    lang = st.radio("Harshe:", ["Hausa", "English"], horizontal=True)
    placeholder = "Yaya zan duba PVC dina a Bauchi?" if lang=="Hausa" else "How to check my PVC in Bauchi?"
    q = st.text_area("Tambayarka:", placeholder=placeholder)
    if st.button("🚀 Aika Tambaya", use_container_width=True):
        if q.strip():
            add_q(q.strip())
            st.success("✅ Tambayarka ta tafi! Amsa zata bayyana anan kai tsaye da murya.")
            st.balloons()
            st.rerun()
        else:
            st.warning("Rubuta tambaya")

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
                st.write("Duk tambayoyi:")
                for r in rows[-5:]:
                    st.text(f"{r[0]} -> {r[1]}")
        else:
            st.warning(f"Akwai {len(pending)} sabuwar tambaya tana jira ka")
            for idx, r in pending:
                st.markdown(f"**Tambaya #{idx+1}:** {r[0]}")
                st.caption(f"Lokaci: {r[2]}")
                ans = st.text_area(f"Rubuta Amsa kai tsaye:", key=f"adm_{idx}", placeholder="Amsarka a nan...")
                colA, colB = st.columns(2)
                with colA:
                    if st.button(f"✅ Buga Kai Tsaye + Sauti", key=f"btn_{idx}", use_container_width=True):
                        if ans.strip():
                            add_a(idx, ans.strip())
                            st.success(f"🔥 YES! Amsa ta shiga app kai tsaye! Jama'a na iya jin ta da murya yanzu! (Row {idx})")
                            st.balloons()
                            st.rerun()
                with colB:
                    if ans.strip():
                        if st.button(f"🔊 Gwada Sauti", key=f"test_{idx}"):
                            speak(ans.strip(), f"test_{idx}.mp3")
                st.markdown("---")
    elif pw != "":
        st.error("Password kuskure! Saka: bauchi2027")", layout="centered")

# Background picture logic - will work on phone and laptop
def get_img_as_base64(file):
    try:
        with open(file, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return None

img_base64 = get_img_as_base64("logo.png")

bg_style = ""
if img_base64:
    bg_style = f"""
    background-image: url("data:image/png;base64,{img_base64}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    """
else:
    bg_style = "background: white;"

st.markdown(f"""
<style>
h1 {{ color: #008751; }}
.stButton>button {{ background-color: #008751; color: white; border-radius: 8px; padding: 0.5em 1em; }}
.murya-header {{
    text-align: center;
    padding: 2.5rem 1rem;
    border: 3px solid #008751;
    border-radius: 12px;
    margin-bottom: 1.2rem;
    {bg_style}
}}
.murya-overlay {{
    background: rgba(255,255,255,0.85);
    padding: 1rem;
    border-radius: 8px;
    display: inline-block;
}}
.murya-title {{
    font-size: 3rem;
    font-weight: 900;
    color: black;
    letter-spacing: 4px;
    margin: 0;
}}
.murya-title span {{ color: #008751; }}
</style>
<div class="murya-header">
    <div class="murya-overlay">
        <div class="murya-title">MUR<span>YA</span></div>
        <div style="font-size:0.8rem;color:#008751;font-weight:bold;">NIGERIA • INEC STYLE • BAUCHI</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.title("Murya")
st.markdown("Ref: Zaharaddeen Muhammad | Bauchi | AI4Elections")
st.markdown("---")

questions = ["Yaushe ne zaben 2027?", "Ta yaya zan yi rajista don zabe?", "Ina zan kada kuri'ata?", "Wane takarda ake bukata?", "Yaushe ne ranar karshe ta rajista?"]
selected = st.selectbox("Zabi tambaya daga nan:", questions)

answers = {
    "Yaushe ne zaben 2027?": "Zaben Najeriya zai gudana a watan Janairu - Fabrairu 2027. Hukumar INEC zata sanar da takamaiman rana. Bi www.inecnigeria.org don sabuntawa.",
    "Ta yaya zan yi rajista don zabe?": "Je zuwa ofishin INEC mafi kusa da kai ko ka yi rajista online a cvr.inecnigeria.org. Ka tafi da katin dan kasa ko takardar shaida.",
    "Ina zan kada kuri'ata?": "Zaka kada kuri'a a rumfar zaben da ka yi rajista. Duba katin zabenka (PVC) don wurin rumfarka.",
    "Wane takarda ake bukata?": "Katin Zabe (PVC) shine mafi muhimmanci. Idan baka da shi, ka je INEC don sabon kati kafin ranar karshe.",
    "Yaushe ne ranar karshe ta rajista?": "INEC zata sanar da ranar karshe. Yawanci watanni 6 kafin zabe. Kada ka jira!"
}

current_answer = answers.get(selected)
st.info(current_answer)

if st.button("Saurara a Hausa"):
    with st.spinner("Ana shirya murya..."):
        try:
            tts = gTTS(text=current_answer, lang='ha')
            tts.save("murya.mp3")
        except:
            tts = gTTS(text=current_answer, lang='en')
            tts.save("murya.mp3")
        st.audio("murya.mp3", format="audio/mp3")

st.markdown("---")
st.text_area("Rubuta tambayarka:", placeholder="Misali: Yaya zan canza wurin zabe na?")
st.button("Aika Tambaya")
st.caption("Uses only public INEC data | No phone data stored | Responsible AI | Made in Bauchi")