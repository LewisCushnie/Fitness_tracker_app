import streamlit as st
import utils.data_download as dd
from datetime import date


st.set_page_config(
    page_title="Fitness Tracker App",
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

st.title('Fitness Stats')
line = '---'
st.markdown(line)

# get current date
current_date = date.today()

# get strava data from the api
activities = dd.get_strava_data(current_date)

st.write(activities)
