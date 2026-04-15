import streamlit as st

st.title("🎙️ Teste do Microfone")
audio_file = st.audio_input("Gravar áudio")
audio_bytes = audio_file.getvalue() if audio_file else None

if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")
