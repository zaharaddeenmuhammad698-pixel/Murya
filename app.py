import streamlit as st
import csv, os
from datetime import datetime
from gtts import gTTS

st.set_page_config(page_title="Murya - Bauchi Voice", layout="centered", page_icon="🎙️")

os.makedirs("voice_notes/incoming", exist_ok=True)
os.makedirs("voice_notes/replies", exist_ok=True)

st.markdown("""
<style>
.big-title {font-size:32px; font-weight:bold; color:#006400; text-align:center;}
.subtitle {text-align:center; color:#555; font-size:13px;}
.card {background:#f0fdf4; padding:15px; border-radius:12px; border:1px solid #bbf7d0; margin:10px 0;}
.footer {text-align:center; padding:20px; background:#f0fdf4; border-radius:12px; margin-top:30px; border:1px solid #bbf7d0;}

/* --- PROFESSIONAL VOICE HOLDER --- */
.voice-holder {
    background: linear-gradient(135deg, #006400 0%, #228B22 100%);
    padding: 25px;
    border-radius: 20px;
    text-align: center;
    color: white;
    margin: 15px 0;
    box-shadow: 0 8px 20px rgba(0,100,0,0.3);
}
.voice-holder h2 {color: white !important; font-size: 26px; margin: 0;}
.voice-holder p {color: #e0ffe0; font-size: 16px; margin: 5px 0;}
.step-box {
    background: white;
    color: #006400;
    padding: 12px;
    border-radius: 12px;
    margin: 10px 0;
    font-weight: bold;
    font-size: 18px;
    border-left: 6px solid #FFD700;
    text-align: left;
}
.pulse {
    animation: pulse 1.5s infinite;
}
@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
}
/* Make the audio_input BIG */
div[data-testid="stAudioInput"] {
    background: white;
    padding: 15px;
    border-radius: 15px;
    border: 3px dashed #FFD700;
}
div[data-testid="stAudioInput"] button {
    background: #006400 !important;
    color: white !important;
    height: 70px !important;
    font-size: 20px !important;
    border-radius: 12px !important;
    width: 100% !important;
}
</style>
<div class="big-title">🎙️ MURYA</div>
<div class="subtitle">Muryar Zabe - Bauchi | Zaharaddeen Muhammad | AI4Elections</div>
""", unsafe_allow_html=True)

FILE = "murya_strong.csv"
if not os.path.exists(FILE):
    with open(FILE, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(["tambaya","amsa","lokaci","status"])

FAQ_4 = [
    {"q": "Ta yaya zan duba katin zabe na na dindindin?", "a": "Je zuwa shafin ofishin Hukumar zabe Mai zaman kanta ta ka sa (inec.gov.ng). ko ka je ofishin ta mafi kusa da kai a Bauchi. Tafi da lambar shaida na mai zabe na ka."},
    {"q": "Yaushe zaben 2027 zai gudana?", "a": "Zaben gama garin zai gudana ne a watan janairun 2027. Murya zata sanar da kai da zarar Hukumar zabe Mai zaman kanta ta ka sa ta yi Wani sauyi. Ka guji labaran karya."},
    {"q": "Ina zan karbi katin zabe na dindindin dina a Bauchi?", "a": "A ofishin Hukumar zabe Mai zaman kanta ta ka sa na karamar hukumar ka a Bauchi. Dole sai da katin dan kasa ko da katin zabe na wucen gadi."},
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

def clean_for_voice(text):
    text = text.replace("voters.inecnigeria.org", "shafin INEC").replace("www.", "").replace("https://", "").replace("http://", "")
    for k, v in {"PVC": " P V C ", "INEC": " I N E C "}.items():
        text = text.replace(k, v).replace(k.lower(), v).replace(k.capitalize(), v)
    return text

def detect_by_text(text):
    t = text.lower().strip().replace("?"," ").replace("."," ").replace("!"," ").replace(","," ").replace("'"," ")
    words = t.split()
    hausa_dict = ["yaya","ina","me","mene","wanene","yaushe","zan","zai","nan","ni","kai","suna","muna","don","kuma","amma","daga","ba","ne","ce","da","shin","zabe","bauchi"]
    return "ha" if sum(1 for w in words if w in hausa_dict) >= 1 else "en"

def speak_auto(text, name):
    cleaned = clean_for_voice(text)
    lang = detect_by_text(text)
    try:
        gTTS(cleaned, lang=lang, slow=False).save(name)
        st.audio(name)
    except:
        try:
            gTTS(cleaned, lang="en", slow=False).save(name)
            st.audio(name)
        except:
            st.caption("🔊 Sauti na bukatar internet kadan")

tab_info, tab_ask, tab_admin = st.tabs(["📌 Bayanan INEC", "👥 Tambaya + Sauti", "🔐 Admin"])

with tab_info:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("✅ Bayanan INEC Tabbatattu")
    st.markdown("**Murya tana yaki da labaran karya.**\n- ✅ INEC: Zabe 2027 yana nan\n- ✅ PVC collection zai ci gaba\n- ✅ Zaharaddeen ne ya tabbatar")
    st.markdown('</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    data = get_data()
    col1.metric("Tambayoyi", len(data))
    col2.metric("Amsoshi", len([r for r in data if len(r)>1 and r[1].strip()!=""]))
    col3.metric("Jira", len([r for r in data if len(r)<2 or r[1].strip()==""]))
    st.markdown("---")
    st.subheader("📌 FAQ 4")
    for i, faq in enumerate(FAQ_4):
        st.markdown(f"**Q{i+1}: {faq['q']}**")
        st.success(f"A: {faq['a']}")
        if st.button(f"🔊 Sauti", key=f"faq_{i}", use_container_width=True):
            speak_auto(faq['a'], f"faq_{i}.mp3")
        st.markdown("---")

with tab_ask:
    # --- PROFESSIONAL VOICE HOLDER - NEW DESIGN ---
    st.markdown("""
    <div class="voice-holder">
        <h2>🎤 GA WANDA BAI IYA RUBUTU BA</h2>
        <p>Ba sai ka iya rubutu ba! Yi magana kawai kamar WhatsApp</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="step-box">👉 Mataki 1: Danna ja button a kasa</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-box">👉 Mataki 2: Yi magana da Hausa - misali "Ina zan karbi PVC dina?"</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-box">👉 Mataki 3: Danna STOP - Shikenan! An tura</div>', unsafe_allow_html=True)

    # The actual recorder - now inside professional holder
    st.markdown('<div style="background:#fffde7; padding:15px; border-radius:15px; border:2px solid #FFD700;">', unsafe_allow_html=True)
    st.markdown("**🎙️ DANNA NAN DOMIN YI MAGANA:**")
    voice_data = st.audio_input("", key="murya_voice_main")
    st.markdown('</div>', unsafe_allow_html=True)

    if voice_data:
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        fpath = f"voice_notes/incoming/Murya_{ts}.wav"
        with open(fpath, "wb") as f:
            f.write(voice_data.getbuffer())
        st.markdown("""
        <div style="background:#d4edda; padding:20px; border-radius:15px; text-align:center; border:3px solid #006400; margin-top:15px;">
            <h2 style="color:#006400; margin:0;">✅ MUN KARBA!</h2>
            <p style="font-size:18px; color:#155724; font-weight:bold;">Nagode! Muryarka ta tafi. Zaharaddeen zai amsa da muryarsa anjima. Kadawo ka duba amsa a kasa.</p>
        </div>
        """, unsafe_allow_html=True)
        st.audio(fpath)
        st.balloons()

    st.markdown("---")
    st.markdown("### 🔊 Amsoshin Murya Daga Zaharaddeen")
    st.caption("Idan Zaharaddeen ya amsa da murya, zaka ji anan:")
    replies = sorted(os.listdir("voice_notes/replies"), reverse=True)[:5]
    if replies:
        for rf in replies:
            st.success(f"🔊 Amsa daga Zaharaddeen: {rf.replace('.wav','')}")
            st.audio(f"voice_notes/replies/{rf}")
    else:
        st.info("⏳ Babu amsar murya tukuna. Da zarar an amsa, zai bayyana anan da murya.")

    st.markdown("---")
    st.subheader("👥 Amsoshin Rubutu (Ga Masu Iya Karatu)")
    rows = get_data()
    answered = [r for r in rows if len(r)>1 and r[1].strip()!=""]
    if answered:
        for i, r in enumerate(reversed(answered)):
            st.markdown(f"**Q:** {r[0]}")
            st.success(f"**A:** {r[1]}")
            if st.button(f"🔊 Sauti", key=f"ans_{i}", use_container_width=True):
                speak_auto(r[1], f"ans_{i}.mp3")
            st.markdown("---")

    st.markdown("### ✍️ Yi Tambaya da Rubutu (Optional)")
    q = st.text_area("Tambayarka:", placeholder="Yaya zan duba PVC dina a Bauchi?", key="q_box")
    if st.button("🚀 Aika Tambaya", use_container_width=True, type="primary"):
        if q.strip():
            add_q(q.strip())
            st.success("✅ YA TAFI!")
            st.balloons()
            st.rerun()

with tab_admin:
    st.subheader("🔐 Admin - Zaharaddeen")
    pw = st.text_input("Password:", type="password")
    if pw == "bauchi2027":
        st.success("Barka da zuwa!")
        rows = get_data()
        pending = [(i, r) for i, r in enumerate(rows) if len(r)<2 or r[1].strip()==""]
        for idx, r in pending:
            st.markdown(f"**Tambaya #{idx+1}:** {r[0]}")
            ans = st.text_area("Amsa:", key=f"adm_{idx}")
            if st.button(f"✅ Buga", key=f"btn_{idx}", use_container_width=True, type="primary"):
                if ans.strip():
                    add_a(idx, ans.strip())
                    st.rerun()
            st.markdown("---")

        st.markdown("---")
        st.markdown("#### 🎧 Sakonnin Murya - Amsa da Muryarka")
        incoming = sorted(os.listdir("voice_notes/incoming"), reverse=True)
        if not incoming:
            st.info("Babu sakon murya")
        else:
            for f in incoming:
                st.markdown(f"**📩 {f}**")
                ipath = f"voice_notes/incoming/{f}"
                rpath = f"voice_notes/replies/{f}"
                st.audio(ipath)
                if os.path.exists(rpath):
                    st.success("Ka riga ka amsa:")
                    st.audio(rpath)
                
                st.markdown("**🎤 Amsa da Muryarka (Professional Reply):**")
                # Professional admin holder too
                st.markdown('<div style="background:#e8f5e9; padding:10px; border-radius:10px;">', unsafe_allow_html=True)
                reply_voice = st.audio_input(f"Danna ka yi reply da murya", key=f"reply_{f}")
                st.markdown('</div>', unsafe_allow_html=True)
                if reply_voice:
                    with open(rpath, "wb") as out:
                        out.write(reply_voice.getbuffer())
                    st.success("✅ An tura amsar murya!")
                    st.audio(rpath)
                    st.rerun()
                st.markdown("---")
    elif pw != "":
        st.error("Password kuskure!")

st.markdown("<div class='footer'><p style='font-weight:bold; color:#006400;'>🎙️ MURYA - Muryar Zabe</p><p>Powered by Zaharaddeen | Bauchi</p></div>", unsafe_allow_html=True)