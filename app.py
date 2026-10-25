import streamlit as st

st.set_page_config(
    page_title="Murya - Tambayoyi kan Zabe",
    layout="centered"
)

st.markdown("""
<style>
h1 { color: #008751; }
.stButton>button { background-color: #008751; color: white; border-radius: 8px; padding: 0.5em 1em; }
</style>
""", unsafe_allow_html=True)

st.title("Murya")
st.markdown("Ref: Zaharaddeen Muhammad | Bauchi | AI4Elections")
st.markdown("---")

st.markdown("### Zabi tambaya:")

questions = [
    "Yaushe ne zaben 2027?",
    "Ta yaya zan yi rajista don zabe?",
    "Ina zan kada kuri'ata?",
    "Wane takarda ake bukata?",
    "Yaushe ne ranar karshe ta rajista?"
]

selected = st.selectbox("Zabi tambaya daga nan:", questions)

st.markdown("### Amsa:")

answers = {
    "Yaushe ne zaben 2027?": "Zaben Najeriya zai gudana a watan Janairu - Fabrairu 2027. Hukumar INEC zata sanar da takamaiman rana. Bi www.inecnigeria.org don sabuntawa.",
    "Ta yaya zan yi rajista don zabe?": "Je zuwa ofishin INEC mafi kusa da kai ko ka yi rajista online a cvr.inecnigeria.org. Ka tafi da katin dan kasa ko takardar shaida.",
    "Ina zan kada kuri'ata?": "Zaka kada kuri'a a rumfar zaben da ka yi rajista. Duba katin zabenka (PVC) don wurin rumfarka.",
    "Wane takarda ake bukata?": "Katin Zabe (PVC) shine mafi muhimmanci. Idan baka da shi, ka je INEC don sabon kati kafin ranar karshe.",
    "Yaushe ne ranar karshe ta rajista?": "INEC zata sanar da ranar karshe. Yawanci watanni 6 kafin zabe. Kada ka jira!"
}

st.info(answers.get(selected))

if st.button("Saurara a Hausa"):
    st.success(answers.get(selected))

st.markdown("---")
st.markdown("**Sako:**")
st.text_area("Rubuta tambayarka:", placeholder="Misali: Yaya zan canza wurin zabe na?")
st.button("Aika Tambaya")

st.markdown("---")
st.caption("Uses only public INEC data | No phone data stored | Responsible AI | Made in Bauchi")