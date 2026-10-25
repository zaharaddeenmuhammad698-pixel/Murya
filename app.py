import streamlit as st
from gtts import gTTS
import base64

st.set_page_config(page_title="Murya - Tambayoyi kan Zabe", layout="centered")

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