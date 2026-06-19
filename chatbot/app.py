import streamlit as st

st.set_page_config(
    page_title="Japan Politics Chatbot",
    page_icon="🇯🇵",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# UI
st.title("Japan Politics Chatbot")

language_options = ["NL", "EN"]
language = st.selectbox("Choose a Language", language_options, index=0)

# Button to switch page
col1, col2, col3 , col4, col5 = st.columns(5)

with col1:
    pass
with col2:
    pass
with col4:
    pass
with col5:
    pass
with col3 :
    if st.button("Start chat"):
        # Switch to the selected page
        st.session_state.language = language
        st.switch_page("pages/chatbot.py")