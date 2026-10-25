import streamlit as st
import csv, os, re
from datetime import datetime
from gtts import gTTS
import pandas as pd

st.set_page_config(page_title="MURYA - INEC x Bauchi Dashboard", layout="wide", page_icon="🎙️")

st.markdown("""
<style>
header[data-testid="stHeader"], div[data-testid="stToolbar"], footer {display:none !important;}
.block-container {padding-top:0.4rem !important; max-width:1400px;}
.top-nav {background:white; padding:10px 16px; border-radius:14px; border:1px solid #c8e6c9; box-shadow:0 2px 10px rgba(0,0,0,0.06); display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;}
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
.chat-wrap {background:#efeae2; padding:10px; border-radius:10px; border:1px solid #d1d7db; height:560px; overflow-y:auto;}
.bubble-user {background:#d9fdd3; padding:7px 10px; border-radius:12px 12px 0 12px; margin:6px 0 6px 10%; font-size:12px; box-shadow:0 1px 0.5px rgba(0,0,0,0.13);}
.bubble-admin {background:white; padding:7px 10px; border-radius:12px 12px 12px 0; margin:6px 10% 6px 0; font-size:12px; box-shadow:0 1px 0.5px rgba(0,0,0,0.13);}
.bubble-meta {font-size:9px; color:#667781; text-align:right; margin-top:2px;}
.admin-on {background:#1b5e20; color:white; padding:4px 10px; border-radius:20px; font-size:11px; font-weight:700;}
</style>
""", unsafe_allow_html=True)

# --- PROFESSIONAL SETUP (YOUR UNBREAKABLE VERSION) ---
os.makedirs("voice_notes/incoming", exist_ok=True)
os.makedirs("voice_notes/replies", exist_ok=True)
FILE="murya_strong.csv"

def init_csv():
    if not os.path.exists(FILE):
        try:
            with open(FILE,"w",newline="",encoding="utf-8") as f: csv.writer(f).writerow(["tambaya","amsa","lokaci","status"])
        except: pass
init_csv()

def get_data():
    if not os.path.exists(FILE): return []
    try:
        with open(FILE,"r",encoding="utf-8") as f:
            rows=list(csv.reader(f)); return rows[1:] if len(rows)>1 else []
    except: return []

def add_q(t):
    t=t.strip()[:500]
    if not t: return
    try:
        with open(FILE,"a",newline="",encoding="utf-8") as f: csv.writer(f).writerow([t,"",datetime.now().strftime("%Y-%m-%d %H:%M"),"NEW"])
    except: pass

def add_a(idx,a):
    try:
        data=get_data()
        if 0<=idx<len(data):
            data[idx][1]=a.strip()[:1000]
            data[idx][2]=datetime.now().strftime("%Y-%m-%d %H:%M")
            data[idx][3]="ANSWERED"
        with open(FILE,"w",newline="",encoding="utf-8") as f:
            w=csv.writer(f); w.writerow(["tambaya","amsa","lokaci","status"]); w.writerows(data)
    except: pass

def delete_q(idx):
    try:
        data=get_data()
        if 0<=idx<len(data): data.pop(idx)
        with open(FILE,"w",newline="",encoding="utf-8") as f:
            w=csv.writer(f); w.writerow(["tambaya","amsa","lokaci","status"]); w.writerows(data)
        return True
    except: return False

def clean_for_voice(text):
    text=text.replace("voters.inecnigeria.org","shafin INEC").replace("www.","").replace("https://","").replace("http://","")
    for k,v in {"PVC":" P V C ","INEC":" I N E C ","VIN":" V I N ","LGA":" L G A ","PU":" P U "}.items():
        text=text.replace(k,v).replace(k.lower(),v).replace(k.capitalize(),v)
    return text

def detect_by_text(text):
    t=text.lower().strip().replace("?"," ").replace("."," ").replace("!"," ").replace(","," ").replace("'"," ")
    words=t.split()
    hausa_dict=["yaya","ina","me","mene","menene","wanene","yaushe","yau","gobe","jiya","zan","zai","zaa","nan","can","su","mu","ku","ni","kai","ke","ita","shi","suna","muna","kuna","yake","nake","take","don","domin","kuma","amma","idan","sai","daga","zuwa","cikin","akan","ba","ne","ce","da","ko","shin","eh","a'a","gaskiya","lafiya","gida","aiki","makaranta","kudi","zabe","bauchi","karbi","duba","tafi","je","zo","nawa","yanzu","tukuna","kawai","tambaya","amsa","katin","zabe","dindindin","kasa"]
    return "ha" if sum(1 for w in words if w in hausa_dict)>=1 else "en"

def speak_auto(text,name):
    try:
        gTTS(clean_for_voice(text),lang=detect_by_text(text),slow=False).save(name); st.audio(name)
    except:
        try: gTTS(clean_for_voice(text),lang="en",slow=False).save(name); st.audio(name)
        except: st.caption("🔊 Sauti na bukatar internet kadan")

# --- SESSION STATE (PROFESSIONAL) ---
if "menu_open" not in st.session_state: st.session_state.menu_open=False
if "page" not in st.session_state: st.session_state.page="About Us"
if "voice_key" not in st.session_state: st.session_state.voice_key=0
if "just_sent" not in st.session_state: st.session_state.just_sent=False
if "last_q" not in st.session_state: st.session_state.last_q=""
if "clear_flag" not in st.session_state: st.session_state.clear_flag=None
if "voice_sent" not in st.session_state: st.session_state.voice_sent=False
if "last_voice" not in st.session_state: st.session_state.last_voice=""
if "admin_pw" not in st.session_state: st.session_state.admin_pw=""
IS_ADMIN = st.session_state.get("admin_pw","") == "bauchi2027"

# --- TOP NAV WITH HAMBURGER (LIKE YOUR SCREENSHOT) ---
c1,c2=st.columns([5,1])
with c1:
    st.markdown('<div class="logo-text"><b>✓ INEC | 🎙️ MURYA</b><br><span>Muryar Zabe - Bauchi | Civic Tech • Citizen Voices • Transparent Elections</span></div>', unsafe_allow_html=True)
with c2:
    if st.button("☰", key="ham", use_container_width=True):
        st.session_state.menu_open = not st.session_state.menu_open

if st.session_state.menu_open:
    st.markdown('<div class="menu-box">', unsafe_allow_html=True)
    st.markdown("**Menu — Danna don buɗewa (like your image: Home, About Us, Contact):**")
    items=["About Us","Dashboard","Bayanan INEC","Chat (Text + Murya)","Charts & Analytics","Admin Login","Contact"]
    cols=st.columns(2)
    for i,it in enumerate(items):
        with cols[i%2]:
            if st.button(f"{'✅ ' if st.session_state.page==it else ''}{it}", key=f"m_{it}", use_container_width=True, type="primary" if st.session_state.page==it else "secondary"):
                st.session_state.page=it; st.session_state.menu_open=False; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- ABOUT US (FIRST PAGE WHEN USER ENTERS) ---
if st.session_state.page=="About Us":
    st.markdown("""
    <div class="about-hero">
    <h2 style="margin:0; color:white;">🎙️ MURYA - Muryar Zabe</h2>
    <p style="margin:8px 0 0 0; font-size:14px; line-height:1.6; color:#e8f5e9;">
    The first voice-based civic tech platform for Bauchi — breaking language & literacy barriers for 2027 elections.<br>
    <b>Track:</b> Electoral Inclusion + Information Integrity | AI4Elections Hackathon 2027 | Bauchi, Nigeria
    </p>
    </div>
    """, unsafe_allow_html=True)
    a,b=st.columns([2,1])
    with a:
        st.markdown("""
        <div class="about-card">
        <div class="section-title">🎯 The Problem</div>
        <p style="font-size:13px; line-height:1.6;">
        In Bauchi, <b>over 40% of voters</b> struggle with English text INEC info. Many cannot read/write but speak Hausa fluently.
        Fake news about PVC & election dates spreads faster than official info. Result: voter apathy & exclusion — especially women, elderly, rural.
        </p>
        <div class="section-title">💡 Our Solution: MURYA</div>
        <p style="font-size:13px; line-height:1.6;">
        <b>Murya (Voice)</b> allows citizens to:<br>
        • Ask in Hausa by <b>text or voice</b> like WhatsApp — press mic<br>
        • Get <b>verified INEC answers</b> — no AI hallucination, Zaharaddeen verifies directly<br>
        • <b>Listen 🔊</b> — TTS for those who cannot read<br>
        • <b>Share verified info</b> — one-click WhatsApp share to fight fake news<br><br>
        <b>Innovation:</b> Unified text+voice timeline, offline-first, 100% human verification, full Hausa dictionary detection.
        </p>
        <div class="section-title">🛠️ How It Works</div>
        <p style="font-size:12px;">1️⃣ Ask (Rubuta ko yi murya) → 2️⃣ Verify (Zaharaddeen checks INEC) → 3️⃣ Answer (Chat + Voice + Share)</p>
        </div>
        """, unsafe_allow_html=True)
    with b:
        st.markdown("""
        <div class="about-card">
        <div class="section-title">📊 Why Bauchi</div>
        <p style="font-size:12px;">• 20 LGAs, 5.1M+ voters<br>• High Hausa-speaking<br>• Low digital literacy<br>• High fake news risk in 2027<br><br>Built <b>by Bauchi, for Bauchi</b>.</p>
        <div class="section-title">👤 Team</div>
        <p style="font-size:13px; font-weight:700; color:#006400;">Zaharaddeen Muhammad</p>
        <p style="font-size:11px; color:#555;">Civic Tech Builder | Bauchi<br>Powered by Zaharaddeen Muhammad | Bauchi, Nigeria</p>
        <div style="background:#e8f5e9; padding:8px; border-radius:8px; font-size:11px;">✅ No AI Hallucination — Verified by Zaharaddeen directly from INEC portal.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚀 Open Dashboard →", use_container_width=True, type="primary"):
            st.session_state.page="Dashboard"; st.rerun()
        st.link_button("Sign In (Admin)", "https://eeno.streamlit.app", use_container_width=True)
        st.link_button("Apply Now (Ask Question)", "https://eeno.streamlit.app", use_container_width=True)

# --- DASHBOARD (WHEN CLICK DASHBOARD, SEE REMAINING DECISIONS) ---
elif st.session_state.page=="Dashboard":
    data=get_data(); ans=len([r for r in data if len(r)>1 and r[1].strip()!=""]); pen=len([r for r in data if len(r)<2 or r[1].strip()==""])
    vc=len([f for f in os.listdir("voice_notes/incoming") if f.endswith(".wav")]) if os.path.exists("voice_notes/incoming") else 0
    st.markdown("### 📊 Dashboard — All Decisions Visible")
    m1,m2,m3,m4=st.columns(4)
    with m1: st.markdown(f'<div class="metric-card"><div class="metric-num">{len(data)}</div><div class="metric-lab">TAMBAYOYI</div></div>', unsafe_allow_html=True)
    with m2: st.markdown(f'<div class="metric-card"><div class="metric-num">{ans}</div><div class="metric-lab">AMSOSHI</div></div>', unsafe_allow_html=True)
    with m3: st.markdown(f'<div class="metric-card"><div class="metric-num">{pen}</div><div class="metric-lab">JIRA</div></div>', unsafe_allow_html=True)
    with m4: st.markdown(f'<div class="metric-card"><div class="metric-num">{vc}</div><div class="metric-lab">MURYOYI</div></div>', unsafe_allow_html=True)
    if IS_ADMIN: st.markdown('<div style="margin:8px 0;"><span class="admin-on">🔐 ADMIN MODE ON</span></div>', unsafe_allow_html=True)
    
    l,c,r=st.columns([1.1,1.6,0.9])
    with l:
        st.markdown('<div class="about-card"><div class="section-title">✅ Bayanan INEC Preview</div>INEC: Zabe 2027 yana nan, PVC collection zai ci gaba.
INEC ta tabbatar da haka daga ran 9 gawata oktoban 2027 — yaki da labaran karya.</div>', unsafe_allow_html=True)
        FAQ_4=[
         {"q":"Ta yaya zan duba PVC?","a":"Je zuwa inec.gov.ng ko ofishin INEC a Bauchi."},
         {"q":"Yaushe zaben 2027?","a":"Janairu 2027."},
         {"q":"Ina zan karbi PVC?","a":"Ofishin INEC na LGA."},
         {"q":"Zan iya zabe ba tare da PVC ba?","a":"A'a! Dole sai da asali."},
        ]
        for i,f in enumerate(FAQ_4): st.markdown(f'<div class="about-card"><b>Q{i+1}: {f["q"]}</b><br><span style="color:#006400;">A: {f["a"]}</span></div>', unsafe_allow_html=True)
    with c:
        st.markdown('<div class="about-card"><div class="section-title">💬 Chat Preview + Voice</div>', unsafe_allow_html=True)
        st.markdown('<div class="voice-tip"><b>🎤 Ga wanda bai iya rubutu ba</b> — kamar WhatsApp.</div>', unsafe_allow_html=True)
        # Minimal chat preview logic (full logic in Chat page)
        for r in get_data()[-5:]:
            st.markdown(f'<div class="bubble-user">{r[0]}</div>', unsafe_allow_html=True)
            if len(r)>1 and r[1].strip(): st.markdown(f'<div class="bubble-admin"><b>Zaharaddeen:</b> {r[1]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        if st.button("Go to Full Chat →", use_container_width=True): st.session_state.page="Chat (Text + Murya)"; st.rerun()
    with r:
        st.markdown('<div class="about-card"><div class="section-title">🔐 Admin Direct Preview</div>', unsafe_allow_html=True)
        st.caption("Login to delete spam from chat")
        st.text_input("Password:", type="password", key="admin_pw", placeholder="bauchi2027")
        if IS_ADMIN: st.success("ADMIN ON — Go to Chat to delete spam")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="about-card"><div class="section-title">📈 Charts Preview</div>', unsafe_allow_html=True)
        if data: st.bar_chart(pd.DataFrame({"Amsoshi":[ans],"Jira":[pen]}).T)
        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page=="Bayanan INEC":
    st.markdown("### 📌 Bayanan INEC + FAQs 4 (Tabbatattu)")
    FAQs_4=[
     {"q":"Ta yaya zan duba katin zabe na na dindindin?","a":"Je zuwa shafin ofishin Hukumar zabe Mai zaman kanta ta ka as (inec.gov.ng) ko ka je ofishin ta mafi kusa da kai a Bauchi."},
     {"q":"Yaushe zaben 2027 zai gudana?","a":"Zaben gama garin zai gudana ne a watan janairun 2027. Murya zata sanar da kai da zarar Hukumar zabe Mai zaman kanta ta ka sa ta yi Wani sauyi."},
     {"q":"Ina zan karbi katin zabe na dindindin dina a Bauchi?","a":"A ofishin Hukumar zabe Mai zaman kanta ta ka sa na karamar hukumar ka a Bauchi."},
     {"q":"Zan iya zabe ba tare da katin zabe na dindindin dina ba?","a":"A'a! Dole sai da katin zabe na asali. Hoton waya ko photocopy ba ya aiki."},
    ]
    for i,faq in enumerate(FAQ_4):
        st.markdown(f'<div class="about-card"><b>Q{i+1}: {faq["q"]}</b><br><span style="color:#006400;">A: {faq["a"]}</span></div>', unsafe_allow_html=True)
        if st.button(f"🔊 Sauti Q{i+1}", key=f"faq_{i}"): speak_auto(faq['a'], f"faq_{i}.mp3")

elif st.session_state.page=="Charts & Analytics":
    st.markdown("### 📈 Charts & Analytics")
    data=get_data()
    if not data: st.info("Babu data tukuna — tambayoyi zasu bayyana a charts anan")
    else:
        ans=len([r for r in data if len(r)>1 and r[1].strip()!=""]); pen=len([r for r in data if len(r)<2 or r[1].strip()==""])
        c1,c2=st.columns(2)
        with c1:
            st.markdown('<div class="about-card"><div class="section-title">Status</div>', unsafe_allow_html=True)
            st.bar_chart(pd.DataFrame({"Amsoshi":[ans],"Jira":[pen]}))
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="about-card"><div class="section-title">Growth</div>', unsafe_allow_html=True)
            st.line_chart(pd.DataFrame({"Tambayoyi": list(range(1, len(data)+1))}))
            st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page.startswith("Chat"):
    st.markdown("### 💬 Chat — Text + Murya Joined (Kamar WhatsApp) — Professional Version")
    st.markdown('<div class="voice-tip"><b>🎤 Ga wanda bai iya rubutu ba</b> — matsa mic ka yi magana kamar WhatsApp. An hada rubutu + murya a wuri daya.</div>', unsafe_allow_html=True)
    if st.session_state.just_sent: st.success(f"✅ YA TAFI! '{st.session_state.last_q}'"); st.balloons(); st.session_state.just_sent=False
    if st.session_state.voice_sent: st.success(f"✅ MUN KARBA MURYARKA! {st.session_state.last_voice}"); st.balloons(); st.session_state.voice_sent=False
    if st.session_state.clear_flag=="text" and "q_box" in st.session_state: st.session_state.q_box=""; st.session_state.clear_flag=None
    if st.session_state.clear_flag=="voice": st.session_state.voice_key+=1; st.session_state.clear_flag=None

    ct,cv=st.columns([2,1])
    with ct:
        lang=st.radio("Harshe:",["Hausa","English"],horizontal=True,key="lang_choice")
        placeholder="Yaya zan duba PVC dina a Bauchi?" if lang=="Hausa" else "Please check my PVC status in Bauchi"
        q=st.text_area("Tambayarka:", placeholder=placeholder, key="q_box", height=70, label_visibility="collapsed")
        if st.button("🚀 Aika Tambaya", use_container_width=True, type="primary"):
            if q.strip(): add_q(q.strip()); st.session_state.last_q=q.strip(); st.session_state.just_sent=True; st.session_state.clear_flag="text"; st.rerun()
    with cv:
        st.caption("🎤 Murya:")
        voice_data=st.audio_input("", key=f"murya_{st.session_state.voice_key}", label_visibility="collapsed")
        if voice_data is not None:
            if len(voice_data.getbuffer())>10*1024*1024: st.error("Muryar ta yi yawa - kasa da 10MB")
            else:
                ts=datetime.now().strftime("%Y-%m-%d_%H-%M-%S"); fpath=f"voice_notes/incoming/Murya_{ts}.wav"
                with open(fpath,"wb") as f: f.write(voice_data.getbuffer())
                st.session_state.last_voice=f"Murya_{ts}.wav"; st.session_state.voice_sent=True; st.session_state.clear_flag="voice"; st.rerun()

    chat_items=[]; rows=get_data()
    for idx,r in enumerate(rows):
        try: t=datetime.strptime(r[2],"%Y-%m-%d %H:%M") if len(r)>2 and r[2] else datetime.min
        except: t=datetime.min
        chat_items.append({"kind":"text","time":t,"idx":idx,"q":r[0],"a":r[1] if len(r)>1 else "","time_str":r[2] if len(r)>2 else ""})
    try:
        for fname in os.listdir("voice_notes/incoming"):
            if not fname.endswith(".wav"): continue
            try: m=re.search(r"(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})",fname); t=datetime.strptime(m.group(1),"%Y-%m-%d_%H-%M-%S") if m else datetime.min
            except: t=datetime.min
            chat_items.append({"kind":"voice","time":t,"fname":fname,"incoming":f"voice_notes/incoming/{fname}","reply":f"voice_notes/replies/{fname}"})
    except: pass
    chat_items=sorted(chat_items,key=lambda x:x["time"])

    st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
    if not chat_items: st.caption("Babu sakonni tukuna — ka fara tambaya a sama.")
    else:
        for item in chat_items[-40:]:
            if item["kind"]=="text":
                st.markdown(f'<div class="bubble-user"><div style="font-weight:600; font-size:10px;">Kai:</div>{item["q"]}<div class="bubble-meta">{item["time_str"]} ✓✓</div></div>', unsafe_allow_html=True)
                c1,c2,c3=st.columns([1,1,1])
                with c1:
                    safe_q=item['q'].replace(' ','%20')[:400]
                    st.link_button("🔗 Share", f"https://wa.me/?text=Murya%20Bauchi%20-%20Q:%20{safe_q}", key=f"sh_{item['idx']}_{item['time']}")
                with c2:
                    if st.button("🔊 Sauti", key=f"sp_{item['idx']}_{item['time']}"): speak_auto(item['q'], f"q_{item['idx']}.mp3")
                if IS_ADMIN:
                    with c3:
                        if st.button("🗑️ Delete", key=f"del_{item['idx']}_{item['time']}", help="Admin only - delete spam"):
                            delete_q(item["idx"]); st.toast("An goge!"); st.rerun()
                if item["a"].strip():
                    st.markdown(f'<div class="bubble-admin"><b>Zaharaddeen:</b> {item["a"]}<div class="bubble-meta">{item["time_str"]}</div></div>', unsafe_allow_html=True)
                    if st.button("🔊 Amsa", key=f"spa_{item['idx']}_{item['time']}", use_container_width=True): speak_auto(item["a"], f"ans_{item['idx']}.mp3")
            else:
                if not os.path.exists(item["incoming"]): continue
                st.markdown(f'<div class="bubble-user">🎤 Sakon Murya<div class="bubble-meta">{item["fname"]} ✓✓</div></div>', unsafe_allow_html=True)
                st.audio(item["incoming"])
                cv1,cv2=st.columns([1,1])
                with cv1: st.link_button("🔗 Share", "https://wa.me/?text=Murya%20Bauchi%20-%20Sakon%20Murya%20-%20Verified", key=f"shv_{item['fname']}")
                if IS_ADMIN:
                    with cv2:
                        if st.button("🗑️ Goge Murya", key=f"delv_{item['fname']}"):
                            try:
                                if os.path.exists(item["incoming"]): os.remove(item["incoming"])
                                if os.path.exists(item["reply"]): os.remove(item["reply"])
                                st.toast("An goge muryar!"); st.rerun()
                            except: pass
                if os.path.exists(item["reply"]):
                    st.markdown(f'<div class="bubble-admin">🎙️ Amsar Murya</div>'); st.audio(item["reply"])
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page=="Admin Login":
    st.markdown("### 🔐 Admin Login — Direct Access (Professional)")
    pw=st.text_input("Password:", type="password", key="admin_pw", placeholder="bauchi2027")
    if pw=="bauchi2027":
        st.success("✅ ADMIN ON — Yanzu zaka iya goge spam daga Chat + Amsa")
        rows=get_data()
        pending=[(i,r) for i,r in enumerate(rows) if len(r)<2 or r[1].strip()==""]
        if not pending: st.info("Babu sabbin tambayoyi — duk an amsa!")
        else:
            st.warning(f"{len(pending)} sabuwar tambaya tana jira")
            for idx,r in pending[:10]:
                col1,col2=st.columns([4,1])
                with col1: st.markdown(f"**#{idx+1}: {r[0][:80]}** — {r[2]}")
                with col2:
                    with st.popover("⋮"):
                        if st.button("🗑️ Delete", key=f"delA_{idx}", use_container_width=True):
                            delete_q(idx); st.toast("An goge!"); st.rerun()
                ans=st.text_area("Amsa:", key=f"adm_{idx}", height=70, placeholder="Rubuta amsa...")
                if st.button("✅ Buga Kai Tsaye", key=f"btn_{idx}", type="primary", use_container_width=True):
                    if ans.strip(): add_a(idx,ans.strip()); st.balloons(); st.rerun()
                st.markdown("---")
        st.markdown("---")
        st.subheader("🎧 Muryoyi - Amsa da Murya")
        for f in sorted(os.listdir("voice_notes/incoming"), reverse=True)[:10]:
            ipath=f"voice_notes/incoming/{f}"; rpath=f"voice_notes/replies/{f}"
            if not os.path.exists(ipath): continue
            st.write(f"📩 {f}"); st.audio(ipath)
            if os.path.exists(rpath): st.audio(rpath)
            rv=st.audio_input("🎤 Amsa da murya", key=f"reply_{f}")
            if rv is not None:
                with open(rpath,"wb") as out: out.write(rv.getbuffer())
                st.success("✅ Amsa ta tafi!")
    elif pw!="": st.error("Password kuskure!")

elif st.session_state.page=="Contact":
    st.markdown("""
    <div class="about-card">
    <div class="section-title">📞 Contact Us</div>
    <p style="font-size:13px;">
    <b>MURYA - Muryar Zabe Bauchi</b><br>
    Civic Tech Platform • Citizen Voices • Transparent Elections<br><br>
    <b>Powered by Zaharaddeen Muhammad</b><br>
    Bauchi, Nigeria<br><br>
    <b>Track:</b> Electoral Inclusion + Information Integrity<br>
    <b>AI4Elections Hackathon 2027</b><br><br>
    ✅ No AI Hallucination — Every answer verified by human directly from INEC portal.<br><br>
    <b>How to reach us:</b> Use Chat page to ask questions — we reply directly.
    </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center; padding:12px; background:#f0fdf4; border-radius:10px; border:1px solid #bbf7d0; margin-top:16px;">
<p style="font-weight:bold; color:#006400; margin:0;">🎙️ MURYA - Muryar Zabe</p>
<p style="font-size:11px; color:#111; margin:2px 0;"><b>Powered by Zaharaddeen Muhammad | Bauchi, Nigeria | INEC x MURYA</b></p>
</div>
""", unsafe_allow_html=True)