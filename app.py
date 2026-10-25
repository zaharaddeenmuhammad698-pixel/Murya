import streamlit as st
import csv, os, re
from datetime import datetime
from gtts import gTTS

# --- PAGE CONFIG ---
st.set_page_config(page_title="Murya - Bauchi Voice", layout="centered", page_icon="🎙️")

# --- GLOBAL CSS - HIDE FORK + PROFESSIONAL UI ---
st.markdown("""
<style>
header[data-testid="stHeader"], div[data-testid="stToolbar"], footer {display:none !important;}
.big-title {font-size:30px; font-weight:800; color:#006400; text-align:center; margin:0;}
.subtitle {text-align:center; color:#666; font-size:12px; margin-top:2px;}
.card {background:#f0fdf4; padding:14px; border-radius:12px; border:1px solid #bbf7d0; margin:10px 0;}
.footer {text-align:center; padding:18px; background:#f0fdf4; border-radius:12px; margin-top:30px; border:1px solid #bbf7d0;}
.voice-tip {background:#f1f8e9; padding:7px 10px; border-radius:8px; border-left:3px solid #66bb6a; margin:8px 0;}
.voice-tip b {font-size:12px; color:#2e7d32; font-weight:600;}
.voice-tip span {font-size:11px; color:#616161; font-weight:400;}
div[data-testid="stAudioInput"] {background:#ffffff; padding:6px; border-radius:10px; border:2px dashed #a5d6a7;}
.chat-wrap {background:#efeae2; padding:12px; border-radius:12px; border:1px solid #d1d7db; max-height:650px; overflow-y:auto;}
.bubble-user {background:#d9fdd3; padding:8px 11px; border-radius:12px 12px 0 12px; margin:8px 0 8px 15%; box-shadow:0 1px 0.5px rgba(0,0,0,0.13);}
.bubble-admin {background:#ffffff; padding:8px 11px; border-radius:12px 12px 12px 0; margin:8px 15% 8px 0; box-shadow:0 1px 0.5px rgba(0,0,0,0.13);}
.bubble-text {font-size:13px; color:#111b21; line-height:1.35; word-break:break-word;}
.bubble-meta {font-size:10px; color:#667781; text-align:right; margin-top:4px;}
</style>
<div class="big-title">🎙️ MURYA</div>
<div class="subtitle">Muryar Zabe - Bauchi | Zaharaddeen Muhammad | AI4Elections</div>
""", unsafe_allow_html=True)

# --- SAFE DIRS ---
os.makedirs("voice_notes/incoming", exist_ok=True)
os.makedirs("voice_notes/replies", exist_ok=True)

FILE = "murya_strong.csv"

def init_csv():
    if not os.path.exists(FILE):
        try:
            with open(FILE, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(["tambaya","amsa","lokaci","status"])
        except Exception: pass

init_csv()

FAQ_4 = [
    {"q": "Ta yaya zan duba katin zabe na na dindindin?", "a": "Je zuwa shafin ofishin Hukumar zabe Mai zaman kanta ta ka sa (inec.gov.ng). ko ka je ofishin ta mafi kusa da kai a Bauchi. Tafi da lambar shaida na mai zabe naka."},
    {"q": "Yaushe zaben 2027 zai gudana?", "a": "Zaben gama garin zai gudana ne a watan janairun 2027. Murya zata sanar da kai da zarar Hukumar zabe Mai zaman kanta ta ka sa ta yi Wani sauyi. Ka guji labaran karya."},
    {"q": "Ina zan karbi katin zabe na dindindin dina a Bauchi?", "a": "A ofishin Hukumar zabe Mai zaman kanta ta ka sa na karamar hukumar ka a Bauchi. Dole sai da katin dan kasa ko da katin zabe na wucen gadi."},
    {"q": "Zan iya zabe ba tare da katin zabe na dindindin dina ba?", "a": "A'a! Dole sai da katin zabe na asali. Hoton waya ko photocopy ba ya aiki a rumfar zabe."},
]

# --- SAFE DATA FUNCTIONS (UNBREAKABLE) ---
def get_data():
    if not os.path.exists(FILE): return []
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            rows = list(csv.reader(f))
            if not rows: return []
            return rows[1:] if len(rows) > 1 else []
    except Exception:
        return []

def add_q(t):
    t = t.strip()[:500]  # limit to prevent break
    if not t: return
    try:
        with open(FILE, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([t, "", datetime.now().strftime("%Y-%m-%d %H:%M"), "NEW"])
    except Exception as e:
        st.error(f"Error saving: {e}")

def add_a(idx, a):
    try:
        data = get_data()
        if 0 <= idx < len(data):
            data[idx][1] = a.strip()[:1000]
            data[idx][2] = datetime.now().strftime("%Y-%m-%d %H:%M")
            data[idx][3] = "ANSWERED"
        with open(FILE, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["tambaya","amsa","lokaci","status"])
            w.writerows(data)
    except Exception as e:
        st.error(f"Error updating: {e}")

def delete_q(idx):
    try:
        data = get_data()
        if 0 <= idx < len(data):
            data.pop(idx)
            with open(FILE, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["tambaya","amsa","lokaci","status"])
                w.writerows(data)
            return True
    except Exception: pass
    return False

# --- YOUR ORIGINAL VOICE LOGIC - KEPT ---
def clean_for_voice(text):
    text = text.replace("voters.inecnigeria.org", "shafin INEC")
    text = text.replace("www.", "").replace("https://", "").replace("http://", "")
    replacements = {"PVC": " P V C ", "INEC": " I N E C ", "VIN": " V I N ", "LGA": " L G A "}
    for k, v in replacements.items():
        text = text.replace(k, v).replace(k.lower(), v).replace(k.capitalize(), v)
    return text

def detect_by_text(text):
    t = text.lower().strip().replace("?"," ").replace("."," ").replace("!"," ").replace(","," ").replace("'"," ")
    words = t.split()
    hausa_dict = ["yaya","ina","me","mene","menene","wanene","yaushe","yau","gobe","jiya","zan","zai","zaa","nan","can","su","mu","ku","ni","kai","ke","ita","shi","suna","muna","kuna","yake","nake","take","don","domin","kuma","amma","idan","sai","daga","zuwa","cikin","akan","ba","ne","ce","da","ko","shin","eh","a'a","gaskiya","lafiya","gida","aiki","makaranta","kudi","zabe","bauchi","karbi","duba","tafi","je","zo","nawa","yanzu","tukuna","kawai"]
    return "ha" if sum(1 for w in words if w in hausa_dict) >= 1 else "en"

def speak_auto(text, name):
    try:
        cleaned = clean_for_voice(text)
        lang = detect_by_text(text)
        gTTS(cleaned, lang=lang, slow=False).save(name)
        st.audio(name)
    except Exception:
        try:
            gTTS(clean_for_voice(text), lang="en", slow=False).save(name)
            st.audio(name)
        except Exception:
            st.caption("🔊 Sauti na bukatar internet kadan")

# --- SESSION STATE - FOR EMPTY + YA TAFI + NO BALLOON LOOP ---
def init_state():
    if "voice_key" not in st.session_state: st.session_state.voice_key = 0
    if "just_sent" not in st.session_state: st.session_state.just_sent = False
    if "last_q" not in st.session_state: st.session_state.last_q = ""
    if "clear_flag" not in st.session_state: st.session_state.clear_flag = None
    if "voice_sent" not in st.session_state: st.session_state.voice_sent = False
    if "last_voice" not in st.session_state: st.session_state.last_voice = ""

init_state()

# --- TABS ---
tab_info, tab_chat, tab_admin = st.tabs(["📌 Bayanan INEC + FAQ 4", "💬 Chat (Text + Murya)", "🔐 Admin Direct"])

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

with tab_chat:
    st.markdown('<div class="voice-tip"><b>🎤 Ga wanda bai iya rubutu ba</b> <span>— kamar WhatsApp, matsa mic ka yi magana, mu saurara.</span></div>', unsafe_allow_html=True)

    # YA TAFI + EMPTY LOGIC
    if st.session_state.just_sent:
        st.success(f"✅ YA TAFI! '{st.session_state.last_q}'")
        st.balloons()
        st.session_state.just_sent = False
    if st.session_state.voice_sent:
        st.success(f"✅ MUN KARBA MURYARKA! {st.session_state.last_voice}")
        st.balloons()
        st.session_state.voice_sent = False
    if st.session_state.clear_flag == "text" and "q_box" in st.session_state:
        st.session_state.q_box = ""; st.session_state.clear_flag = None
    if st.session_state.clear_flag == "voice":
        st.session_state.voice_key += 1; st.session_state.clear_flag = None

    # INPUT AREA
    col_t, col_v = st.columns([2,1])
    with col_t:
        lang = st.radio("Harshe:", ["Hausa", "English"], horizontal=True, key="lang_choice")
        placeholder = "Yaya zan duba PVC dina a Bauchi?" if lang=="Hausa" else "Please check my PVC status in Bauchi"
        q = st.text_area("Tambayarka:", placeholder=placeholder, key="q_box", height=70)
        if st.button("🚀 Aika Tambaya", use_container_width=True, type="primary"):
            if q.strip():
                add_q(q.strip())
                st.session_state.last_q = q.strip()
                st.session_state.just_sent = True
                st.session_state.clear_flag = "text"
                st.rerun()
            else:
                st.warning("⚠️ Rubuta tambaya da farko")
    with col_v:
        st.caption("🎤 Murya:")
        voice_data = st.audio_input("", key=f"murya_{st.session_state.voice_key}", label_visibility="collapsed")
        if voice_data is not None:
            if len(voice_data.getbuffer()) > 10*1024*1024:
                st.error("Muryar ta yi yawa, yi kasa da 2 mins")
            else:
                ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                fpath = f"voice_notes/incoming/Murya_{ts}.wav"
                try:
                    with open(fpath, "wb") as f: f.write(voice_data.getbuffer())
                    st.session_state.last_voice = f"Murya_{ts}.wav"
                    st.session_state.voice_sent = True
                    st.session_state.clear_flag = "voice"
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    st.markdown("---")
    st.markdown("#### 💬 Zantuka — Rubutu + Murya a wuri daya (Kamar WhatsApp)")

    # BUILD UNIFIED CHAT
    chat_items = []
    rows = get_data()
    for idx, r in enumerate(rows):
        try:
            t = datetime.strptime(r[2], "%Y-%m-%d %H:%M") if len(r)>2 and r[2] else datetime.min
        except: t = datetime.min
        chat_items.append({"kind":"text","time":t,"idx":idx,"q":r[0],"a":r[1] if len(r)>1 else "","time_str":r[2] if len(r)>2 else ""})

    try:
        for fname in os.listdir("voice_notes/incoming"):
            if not fname.endswith(".wav"): continue
            try:
                m = re.search(r"(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})", fname)
                t = datetime.strptime(m.group(1), "%Y-%m-%d_%H-%M-%S") if m else datetime.min
            except: t = datetime.min
            chat_items.append({"kind":"voice","time":t,"fname":fname,"incoming":f"voice_notes/incoming/{fname}","reply":f"voice_notes/replies/{fname}"})
    except: pass

    chat_items = sorted(chat_items, key=lambda x: x["time"])

    st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
    if not chat_items:
        st.caption("Babu sakonni tukuna. Fara da rubutu ko murya a sama.")
    else:
        for item in chat_items[-50:]:
            if item["kind"] == "text":
                st.markdown(f'<div class="bubble-user"><div class="bubble-text">{item["q"]}</div><div class="bubble-meta">{item["time_str"]} ✓✓</div></div>', unsafe_allow_html=True)
                if item["a"].strip():
                    st.markdown(f'<div class="bubble-admin"><div class="bubble-text"><b>Zaharaddeen:</b> {item["a"]}</div><div class="bubble-meta">{item["time_str"]}</div></div>', unsafe_allow_html=True)
            else:
                if not os.path.exists(item["incoming"]): continue
                st.markdown(f'<div class="bubble-user"><div class="bubble-text">🎤 Sakon Murya</div>', unsafe_allow_html=True)
                st.audio(item["incoming"])
                st.markdown(f'<div class="bubble-meta">{item["fname"]} ✓✓</div></div>', unsafe_allow_html=True)
                if os.path.exists(item["reply"]):
                    st.markdown(f'<div class="bubble-admin"><div class="bubble-text">🎙️ Amsar Murya</div>', unsafe_allow_html=True)
                    st.audio(item["reply"])
                    st.markdown(f'<div class="bubble-meta">Amsa ✓✓</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab_admin:
    st.subheader("🔐 Naka Kadai — Amsa Kai Tsaye")
    pw = st.text_input("Password:", type="password", key="admin_pw")
    if pw == "bauchi2027":
        st.success("Barka da zuwa, Zaharaddeen!")
        rows = get_data()
        pending = [(i, r) for i, r in enumerate(rows) if len(r)<2 or r[1].strip()==""]
        if not pending:
            st.info("Babu sabbin tambayoyi — duk an amsa!")
        else:
            st.warning(f"Akwai {len(pending)} sabuwar tambaya tana jira")
            for idx, r in pending:
                col1, col2 = st.columns([5,1])
                with col1: st.markdown(f"**Tambaya #{idx+1}:** {r[0]}")
                with col2:
                    with st.popover("⋮"):
                        st.write(f"Manage #{idx+1}")
                        if st.button("🗑️ Delete", key=f"del_{idx}", use_container_width=True):
                            if delete_q(idx): st.toast("An goge!"); st.rerun()
                ans = st.text_area(f"Rubuta Amsa:", key=f"adm_{idx}")
                if st.button(f"✅ Buga Kai Tsaye", key=f"btn_{idx}", use_container_width=True, type="primary"):
                    if ans.strip(): add_a(idx, ans.strip()); st.success("🔥 YES! Amsa ta shiga app!"); st.balloons(); st.rerun()
                st.markdown("---")

        st.markdown("---")
        st.subheader("🎧 Sakonnin Murya - 3 Dots Delete")
        files = sorted(os.listdir("voice_notes/incoming"), reverse=True)[:20]
        if not files:
            st.info("Babu sakon murya")
        else:
            for f in files:
                ipath = f"voice_notes/incoming/{f}"; rpath = f"voice_notes/replies/{f}"
                if not os.path.exists(ipath): continue
                c1, c2 = st.columns([5,1])
                with c1: st.write(f"📩 {f}")
                with c2:
                    with st.popover("⋮"):
                        if st.button("🗑️ Goge Murya", key=f"delv_{f}", use_container_width=True):
                            try:
                                if os.path.exists(ipath): os.remove(ipath)
                                if os.path.exists(rpath): os.remove(rpath)
                                st.toast("An goge!"); st.rerun()
                            except Exception as e: st.error(str(e))
                        if os.path.exists(rpath) and st.button("🗑️ Goge Amsa", key=f"delr_{f}", use_container_width=True):
                            try: os.remove(rpath); st.toast("An goge amsa!"); st.rerun()
                            except: pass
                st.audio(ipath)
                if os.path.exists(rpath): st.success("Ka riga ka amsa:"); st.audio(rpath)
                rv = st.audio_input(f"🎤 Amsa da muryarka", key=f"reply_{f}")
                if rv is not None:
                    try:
                        with open(rpath, "wb") as out: out.write(rv.getbuffer())
                        st.success("✅ An tura amsar murya!"); st.toast("Amsa ta tafi!")
                    except Exception as e: st.error(str(e))
                st.markdown("---")
    elif pw != "":
        st.error("Password kuskure!")

# --- FOOTER - VISIBLE BLACK TEXT ---
st.markdown("""
<div class='footer'>
<p style='font-weight:bold; color:#006400; margin:0; font-size:18px;'>🎙️ MURYA - Muryar Zabe</p>
<p style='font-size:13px; color:#111111 !important; margin:6px 0; font-weight:600;'>Powered by Zaharaddeen Muhammad | Bauchi, Nigeria</p>
<p style='font-size:12px; color:#333333 !important; margin:8px 0;'>Murya is for people that have language & literacy barriers — Hausa voice 🔊, simple text.</p>
<p style='font-size:11px; color:#555555;'>Track: Electoral Inclusion + Information Integrity | AI4Elections 2027</p>
<p style='font-size:11px; color:#006400; margin-top:10px; font-weight:bold;'>✅ No AI Hallucination — Verified by Zaharaddeen directly</p>
</div>
""", unsafe_allow_html=True)