import streamlit as st
import utils.data_download as dd
import utils.google_sheets_db as gdb
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime, timedelta, date
import sqlite3
import tempfile
import json
import gspread

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

# Apply formatting to page
with open("streamlit_utils/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

CLIENT_ID = st.secrets["CLIENT_ID"]
CLIENT_SECRET = st.secrets["CLIENT_SECRET"]
STRAVA_REFRESH_TOKEN = st.secrets["STRAVA_REFRESH_TOKEN"]

strava_tokens = dd.get_strava_refresh_token(CLIENT_ID, CLIENT_SECRET, STRAVA_REFRESH_TOKEN)

st.write(strava_tokens)

# tfile = tempfile.NamedTemporaryFile(mode="w+")
# st.write(type(tfile))
# temp_cred_file_path = f'{tfile.name}.json'
# st.write(temp_cred_file_path)

# create file from google sheets credentials to authorise with
# config, private_key = gdb._google_creds_as_file()

# with open(temp_cred_file_path, 'a') as cred:
#     json.dump(config, cred)

# f = open(temp_cred_file_path)

google_sheets_df = gdb.get_google_sheets_as_df()

st.write(google_sheets_df)
  
# returns JSON object as 
# a dictionary
# data = json.load(f)

# get current date
current_date = date.today()

st.title('Fitness Stats 🏃 🏋️ 🚴')
st.info("You can't improve what you can't measure...")

# ================================================================
# ================= GET DATA AND SET CONTEXT =====================
# ================================================================

# get strava data from the api
activities = dd.get_strava_data(current_date)

# get maps locations
maps_data = dd.get_key_locations()

tab1, tab2, tab3 = st.tabs(['Daily Form', 'Cardio Analysis', 'Physical Tracking'])

# ================================================================
# ===================== SET GLOBAL VARIABLES =====================
# ================================================================ 

with tab1:

    def weight_form():
        with st.form(key= 'daily form'):

            col1, col2, col3 = st.columns(3)
            integers = range(41)

            with col1:
                weight = st.number_input('Enter mass from today (kg):', step= 0.1)
                n_stretched = st.selectbox('How many times did I stretch:', integers)

            with col2:
                w_pullup = st.number_input('Additional weight for pullup (kg):', step = 1)
                w_bench = st.number_input('Bench press (kg):', step = 1)

            with col3:
                r_pullup = st.selectbox('Reps:', integers, key= 'r_pullup')
                r_bench = st.selectbox('Reps:', integers, key= 'r_bench')

            # Every form must have a submit button.
            submitted = st.form_submit_button("Submit")
            row_to_add = [n_stretched
                        ,weight
                        ,w_pullup
                        ,r_pullup
                        ,w_bench
                        ,r_bench]
            
            if submitted:
                st.success("Submitted!")

                # update the google sheets database with form input
                gdb.update_google_sheets_db(row_to_add, current_date, temp_cred_file_path)
            
            else:
                pass
        
        return weight, n_stretched, submitted

    # weight form to collect weight data
    weight = weight_form()

with tab2:

    line = '---'
    st.header('Set Global Variables')

    # select start and end date range for app widgets
    col1, col2 = st.columns(2)
    with col1:
        d = timedelta(days = 10)
        global_start = st.date_input('Start of timeframe', value = current_date - d)

    with col2:
        global_end = st.date_input('End of timeframe', value= current_date)

    # filter for selected date range
    mask = (activities['date'] >= global_start) & (activities['date'] <= global_end)
    activities = activities.loc[mask]
    # st.write(activities)

    # ================================================================  
    # ====================== SUMMARY STATS ===========================
    # ================================================================  

    line = '---'
    st.markdown(line)
    st.header('Summary Stats For Selected Time Period')

    col1, col2, col3, col4 = st.columns(4)

    # total gym visits over time period
    with col1: 
        count_tokei_start = activities['start_location'].str.count("Tokei").sum()
        count_tokei_end = activities['end_location'].str.count("Tokei").sum()
        total_gym_visits = max(count_tokei_start, count_tokei_end)
        st.metric('Total gym visits', int(total_gym_visits))

    with col2:
        # total number of days I cycled
        count_cycle = activities['type'].str.count("Ride").sum()
        st.metric('Total cycle rides', count_cycle)

    with col3:
        # total distance cycled
        ride_mask = (activities['type'] == 'Ride')
        ride_distance = activities['distance (km)'][ride_mask].sum()
        st.metric('Total distance riden (km)', round(ride_distance, 1))

    with col4:
        # total distance cycled
        run_mask = (activities['type'] == 'Run')
        run_distance = activities['distance (km)'][run_mask].sum()
        st.metric('Total distance run (km)', round(run_distance, 1))

    # ----------------------------------------------------------------
    # ----------------------- COUNTER --------------------------------
    # ----------------------------------------------------------------
    st.write(line)
    st.header('Activity Tracker')

    # group the activities dataframe to get a day-by-day count
    activities_by_date = activities.groupby("date")[["ride_count", "run_count", "tokei_count"]].sum()

    # add emoji columns
    did_run_mask = (activities_by_date['run_count'] >= 1)
    activities_by_date.loc[did_run_mask, 'run'] = '🏃'
    activities_by_date['run'] = activities_by_date['run'].fillna('❌')

    did_tokei_mask = (activities_by_date['tokei_count'] >= 1)
    activities_by_date.loc[did_tokei_mask, 'tokei'] = '🏋️'
    activities_by_date['tokei'] = activities_by_date['tokei'].fillna('❌')

    did_ride_mask = (activities_by_date['ride_count'] >= 1)
    activities_by_date.loc[did_ride_mask, 'ride'] = '🚴'
    activities_by_date['ride'] = activities_by_date['ride'].fillna('❌')

    # transpose the dataframe so time is along the columns
    activities_by_date = activities_by_date[['run', 'tokei', 'ride']].transpose()

    st.write(activities_by_date)

    # ----------------------------------------------------------------
    # ----------------------- DISTANCE -------------------------------
    # ----------------------------------------------------------------

    st.write(line)
    st.header('Distance covered from Running and Riding')

    col1, col2 = st.columns(2)

    with col1:
        chart = alt.Chart(activities).mark_bar().encode(
            x='date:O',
            y='distance (km):Q',
            color='type:N'
        )
        st.altair_chart(chart, use_container_width= True, theme= 'streamlit')

    with col2:
        cumulative_chart = alt.Chart(activities).mark_line(
        ).encode(
            x='date:O',
            y='cumulative_distance:Q',
        )
        st.altair_chart(cumulative_chart, use_container_width= True, theme= 'streamlit')

with tab3:
    # ----------------------------------------------------------------
    # ------------------- WEIGHT TRACKING ----------------------------
    # ----------------------------------------------------------------

    st.header('Physical Tracking')

    # read data from the google sheets 'database'
    google_sheets_df = gdb.read_google_sheets_db(temp_cred_file_path)

    # convert "" cells to NaN
    google_sheets_df = google_sheets_df.mask(google_sheets_df == '')

    # convert date column to datetime
    google_sheets_df['Date'] = pd.to_datetime(google_sheets_df['Date'])
    # set date as index to enable truncate
    google_sheets_df = google_sheets_df.set_index('Date')
    # only return records up to current date
    google_sheets_df = google_sheets_df.truncate(after= current_date)
    # reset index back to allow plotting later
    google_sheets_df = google_sheets_df.reset_index()
    google_sheets_df['Date'] = pd.to_datetime(google_sheets_df['Date'])
    google_sheets_df['Date'] = google_sheets_df['Date'].dt.date

    # specify the rolling average periods of interest
    ma_selections = [5, 10]

    # add the rolling average columns
    columns = []
    for ma in ma_selections:
        column_name = f"MA for {ma} days"
        google_sheets_df[column_name] = google_sheets_df['Mass (kg)'].rolling(window=ma, center=False).mean()
        columns.append(column_name)

    col1, col2 = st.columns(2)

    with col1:
        chart = alt.Chart(google_sheets_df).mark_line().encode(
            x = alt.X('Date:O'),
            y = alt.Y('Mass (kg):Q', scale=alt.Scale(domain=[google_sheets_df['Mass (kg)'].min(), google_sheets_df['Mass (kg)'].max()]))
        )
        st.altair_chart(chart, use_container_width= True, theme= 'streamlit')

    with col2:
        starting_mass = google_sheets_df['Mass (kg)'].iloc[0]
        current_mass = google_sheets_df['Mass (kg)'].loc[google_sheets_df['Date'] == current_date]
        current_mass = current_mass.iloc[0]
        perc_diff = round(((current_mass-starting_mass)/starting_mass)*100, 1)

        st.metric('Current mass (kg)'
                ,current_mass
                ,f'{perc_diff}%')

    st.info('''THE FINAL STEP IS THAT I NEED TO AUTOMATE THE MAIN.PY TO AUTO-UPLOAD
    VIA GITHUB ACTIONS''')
