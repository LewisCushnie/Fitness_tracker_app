import streamlit as st

st.set_page_config(
    page_title="Usage Insights App",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

# Make sure session state is preserved
for key in st.session_state:
    st.session_state[key] = st.session_state[key]

# Apply formatting to page
with open("streamlit_utils/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title('Stock analysis')
line = '---'
st.markdown(line)