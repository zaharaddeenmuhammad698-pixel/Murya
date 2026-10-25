import streamlit as st
from gtts import gTTS

st.set_page_config(page_title="Murya - Ref 37")
st.title("Murya")
st.caption("Ref 37 | Zaharaddeen Muhammad | Bauchi | AI4Elections")

data = {
    "Yaushe ne zaben 2027?": "Zaben Najeriya zai gudana a watan Janairu 2027. Hukumar INEC zata sanar da takamaiman rana.",
    "Ina zan kada kuri'a?": "Duba katin zaben ka/ki. Akwai lambar rumfar zabe a jiki. Ko ka/ki ziyarci shafin inec.gov.ng. Domin neman karin bayani",
    "Menene zan dauka zuwa wajen zabe?": "Dauki katin zaben ka/ki PVC din ka/ki kawai. Kar ka/ki manta.",
    "Yadda ake gujewa labaran karya": "Kada ka/ki yada labari ba tare da tabbatarwa ba. Duba shafin INEC na gaskiya(inec.gov.ng) kafin ka/ki yada."
}

q = st.selectbox("Zabi tambaya:", list(data.keys()))
a = data[q]

st.subheader("Amsa:")
st.info(a)

if st.button("Saurara a Hausa", type="primary"):
    with st.spinner("Ana shirya murya..."):
        tts = gTTS(text=a, lang='ha')
        tts.save("murya.mp3")
    st.audio("murya.mp3")
    st.success("Murya ta yi magana!")

st.divider()
st.write("Uses only public INEC data | No phone data stored | Responsible AI")