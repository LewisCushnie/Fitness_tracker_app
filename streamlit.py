import streamlit as st
import utils.data_download as dd
from datetime import date
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime, timedelta


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
st.info('This application is for tracking my personal activites over time')

# ================================================================
# ================= GET DATA AND SET CONTEXT =====================
# ================================================================

# get current date
current_date = date.today()

# get strava data from the api
activities = dd.get_strava_data(current_date)

# get maps locations
maps_data = dd.get_key_locations()



st.write(activities)

# ================================================================
# ===================== SET GLOBAL VARIABLES =====================
# ================================================================    

line = '---'
st.markdown(line)
st.header('Set Global Variables')

# select start and end date range for app widgets
col1, col2 = st.columns(2)
with col1:
    d = timedelta(days = 30)
    global_start = st.date_input('Start of timeframe', value = current_date - d)

with col2:
    global_end = st.date_input('End of timeframe', value= current_date)

# filter for selected date range
mask = (activities['date'] >= global_start) & (activities['date'] <= global_end)
activities = activities.loc[mask]
# st.write(activities)

# ================================================================
# ========================= PLOTTING =============================
# ================================================================  

# ----------------------------------------------------------------
# ----------------------- SUMMARY STATS --------------------------
# ----------------------------------------------------------------

line = '---'
st.markdown(line)
st.header('Summary Stats')

col1, col2, col3, col4 = st.columns(4)

# total gym visits over time period
with col1: 
    count_tokei_start = activities['start_location'].str.count("Tokei").sum()
    count_tokei_end = activities['end_location'].str.count("Tokei").sum()
    total_gym_visits = max(count_tokei_start, count_tokei_end)
    st.metric('Total gym visits', total_gym_visits)

with col2:
    # total number of days I cycled
    count_cycle = activities['type'].str.count("Ride").sum()
    st.metric('Total days cycled', count_cycle)

with col3:
    # total distance cycled
    ride_mask = (activities['type'] == 'Ride')
    ride_distance = activities['distance (km)'][ride_mask].sum()
    st.metric('Total distance riden (km)', ride_distance)

with col4:
    # total distance cycled
    run_mask = (activities['type'] == 'Run')
    run_distance = activities['distance (km)'][run_mask].sum()
    st.metric('Total distance run (km)', run_distance)

# ----------------------------------------------------------------
# ----------------------- COUNTER --------------------------------
# ----------------------------------------------------------------

st.write(line)
st.header('Count of Activities Over Time')

chart = alt.Chart(activities).mark_tick().encode(
    x=alt.X('date:O',
            title='Count',
            axis=alt.Axis(values=[0], ticks=True, grid=False, labels=False),
            scale=alt.Scale()),
    y='type:N',
    color='type:N'
)

st.altair_chart(chart, use_container_width= True, theme= 'streamlit')

# ----------------------------------------------------------------
# ----------------------- DISTANCE -------------------------------
# ----------------------------------------------------------------

st.write(line)
st.header('Distance covered from Running and Riding')

chart = alt.Chart(activities).mark_bar().encode(
    x='date:O',
    y='distance (km):Q',
    color='type:N'
)

st.altair_chart(chart, use_container_width= True, theme= 'streamlit')

# # Create altair chart
# chart = alt.Chart(TABLE_AND_VIEW_BREAKDOWN_df.reset_index()).transform_fold(
# ['VIEW_COUNT', 'MATERIALIZED_VIEW_COUNT', 'BASE_TABLE_COUNT', 'EXTERNAL_TABLE_COUNT'],
# as_=['TYPE', 'COUNT']
# ).mark_bar().encode(
# x= alt.X('TYPE:N', sort= '-y', axis=alt.Axis(labels=False)),
# y= alt.Y('COUNT:Q'),
# color= 'TYPE:N'
# )

# # Dipslay altair chart
# st.altair_chart(chart, use_container_width= True, theme= 'streamlit')

# # Create altair chart
# chart = alt.Chart(filtered_df.reset_index()).mark_bar().encode(
# x= alt.X('WAREHOUSE_NAME'),
# y= alt.Y('PCT_UTILIZATION:Q', axis= alt.Axis(title= 'Percentage Warehouse Utilisation', format= '%')),
# )

# # Display altair chart
# st.altair_chart(chart, use_container_width= True, theme= 'streamlit')
