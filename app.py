import streamlit as st
import csv, os
from  import datetime
from gtts import gTTS

st.set_page_config(page_title="Murya - Bauchi Voice", layout="centered")

# --- KEEP ALL EMOJIS IN UI ---
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

# --- YOUR 4 FAQ - WITH EMOJIS KEPT ---
FAQ_4 = [
    {"q": "Yaya zan duba PVC dina?", "a": "Je zuwa voters.inecnigeria.org ko ka je ofishin INEC na kusa da kai a Bauchi. Tafi da lambar VIN dinka."},
    {"q": "Yaushe zabe 2027 zai gudana?", "a": "INEC har yanzu ba ta fitar da ranar karshe ba. Murya zata sanar da kai da zarar INEC ta tabbatar. Ka guji labaran karya."},
    {"q": "Ina zan karbi PVC dina a Bauchi?", "a": "A ofishin INEC na karamar hukumar ka. Kowane LGA a Bauchi tana da ofishi. Dole sai da katin dan kasa."},
    {"q": "Zan iya zabe ba tare da PVC ba?", "a": "A'a. Dole sai da PVC na asali. Hoton waya ko photocopy ba ya aiki a rumfar zabe."},
]

def get_data():
    if not os.path.exists(FILE): return []
    with open(FILE, "r", encoding="utf-8") as f:
        return list(csv.reader(f))[1:]

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
        try:
            gTTS(text, lang="ha").save(name)
        except:
            gTTS(text, lang="en").save(name)
        st.audio(name)
    except:
        st.caption("🔊 Sauti na bukatar internet kadan — amma amsa a rubuce tana nan.")

# --- KEEP ALL EMOJIS IN TABS ---
tab_info, tab_ask, tab_admin = st.tabs(["📌 Bayanan INEC + FAQ 4", "👥 Tambaya + Sauti", "🔐 Admin Direct"])

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
    
    st.markdown("---")
    st.subheader("📌 FAQ 4 - Tun Farko (Always There)")
    st.caption("Wadannan 4 tambayoyi ne muka sanya tun farko — suna nan koyaushe.")
    for i, faq in enumerate(FAQ_4):
        st.markdown(f"**Q{i+1}: {faq['q']}**")
        st.success(f"A: {faq['a']}")
        if st.button(f"🔊 Ji Sauti FAQ {i+1}", key=f"faq_{i}"):
            speak(faq['a'], f"faq_{i}.mp3")
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
            c1, c2 = st.columns([1,2])
            with c1:
                if st.button(f"🔊 Sauti", key=f"v_{i}_{r[2] if len(r)>2 else i}"):
                    speak(r[1], f"ans_{i}.mp3")
            with c2:
                st.caption(f"🕒 {r[2] if len(r)>2 else ''} | Status: {r[3] if len(r)>3 else 'ANSWERED'}")
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
        st.error("Password kuskure! Saka: bauchi2027") 