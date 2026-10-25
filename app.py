import streamlit as st
import csv, os
from datetime import datetime
from gtts import gTTS

st.set_page_config(page_title="Murya - Bauchi Voice", layout="centered", page_icon="🎙️")

# --- CREATE VOICE FOLDERS ---
os.makedirs("voice_notes/incoming", exist_ok=True)
os.makedirs("voice_notes/replies", exist_ok=True)

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
    {"q": "Ta yaya zan duba katin zabe na na dindindin?", "a": "Je zuwa shafin ofishin Hukumar zabe Mai zaman   kan ta (inec.gov.ng) ko ka je ofishin ta mafi kusa da kai a Bauchi. Tafi da lambar shaida na mai zabe naka."},
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

tab_info, tab_ask, tab_admin = st.tabs(["📌 Bayanan INEC + FAQ 4", "👥 Tambaya + Sauti", "🔐 Admin Direct"])

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
    st.subheader("📌 FAQ 4 - Tun Farko")
    for i, faq in enumerate(FAQ_4):
        st.markdown(f"**Q{i+1}: {faq['q']}**")
        st.success(f"A: {faq['a']}")
        if st.button(f"🔊 Sauti", key=f"faq_{i}", use_container_width=True):
            speak_auto(faq['a'], f"faq_{i}.mp3")
        st.markdown("---")

with tab_ask:
    # --- VOICE FOR ILLITERATE - CRASH-FREE VERSION ---
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🎤 Ga Wanda Bai Iya Rubutu Ba")
    st.markdown("**Ba sai ka iya rubutu ba!** Danna ka yi magana kamar WhatsApp. Danna mic ka yi recording.")
    st.markdown('</div>', unsafe_allow_html=True)

    voice_data = st.audio_input("🎤 DANNA NAN KA YI MAGANA - Murya")
    
    if voice_data:
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        fpath = f"voice_notes/incoming/Murya_{ts}.wav"
        with open(fpath, "wb") as f:
            f.write(voice_data.getbuffer())
        st.success("✅ Mun karba muryarka! Zaharaddeen zai amsa da muryarsa anjima.")
        st.audio(fpath)
        st.balloons()

    st.markdown("---")
    st.markdown("#### 🔊 Ji Amsoshin Murya Daga Zaharaddeen")
    replies = sorted(os.listdir("voice_notes/replies"), reverse=True)[:5]
    if replies:
        for rf in replies:
            st.caption(f"🔊 Amsa: {rf}")
            st.audio(f"voice_notes/replies/{rf}")
    else:
        st.caption("Babu amsar murya tukuna - da zarar mun amsa zai bayyana anan.")

    st.markdown("---")
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

    st.markdown("### ✍️ Yi Sabuwar Tambaya (Rubutu)")
    if "just_sent" not in st.session_state: st.session_state.just_sent = False
    if "last_q" not in st.session_state: st.session_state.last_q = ""
    if "clear_flag" not in st.session_state: st.session_state.clear_flag = False
    if st.session_state.clear_flag:
        st.session_state.q_box = ""
        st.session_state.clear_flag = False
    if st.session_state.just_sent:
        st.success(f"✅ YA TAFI! '{st.session_state.last_q}'")
        st.balloons()
    q = st.text_area("Tambayarka:", placeholder="Yaya zan duba PVC dina a Bauchi?", key="q_box")
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
            st.info("Babu sabbin tambayoyi")
        else:
            for idx, r in pending:
                st.markdown(f"**Tambaya #{idx+1}:** {r[0]}")
                ans = st.text_area(f"Rubuta Amsa:", key=f"adm_{idx}")
                if st.button(f"✅ Buga Kai Tsaye", key=f"btn_{idx}", use_container_width=True, type="primary"):
                    if ans.strip():
                        add_a(idx, ans.strip())
                        st.success("🔥 YES! Amsa ta shiga app!")
                        st.rerun()
                st.markdown("---")

        st.markdown("---")
        st.markdown("#### 🎧 Sakonnin Murya - Amsa da Muryarka (Professional)")
        incoming = sorted(os.listdir("voice_notes/incoming"), reverse=True)
        if not incoming:
            st.info("Babu sabon sakon murya")
        else:
            for f in incoming:
                st.markdown(f"**📩 {f}**")
                ipath = f"voice_notes/incoming/{f}"
                rpath = f"voice_notes/replies/{f}"
                st.audio(ipath)
                if os.path.exists(rpath):
                    st.success("✅ Ka riga ka amsa:")
                    st.audio(rpath)
                st.write("🎤 **Yi reply da muryarka:**")
                reply_voice = st.audio_input(f"Record reply for {f}", key=f"reply_{f}")
                if reply_voice:
                    with open(rpath, "wb") as out:
                        out.write(reply_voice.getbuffer())
                    st.success("✅ An tura amsar murya! Zai bayyana ga jama'a.")
                    st.audio(rpath)
                    st.rerun()
                st.markdown("---")
    elif pw != "":
        st.error("Password kuskure!")

st.markdown("---")
st.markdown("<div class='footer'><p style='font-weight:bold; color:#006400;'>🎙️ MURYA - Muryar Zabe</p><p>Powered by Zaharaddeen Muhammad | Bauchi</p></div>", unsafe_allow_html=True)