import streamlit as st
import utils.data_download as dd
import utils.google_sheets_db as gdb
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime, timedelta, date
import sqlite3

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

# get current date
current_date = date.today()

# create file from google sheets credentials to authorise with
creds_file = gdb._google_creds_as_file()

creds_file = '''{
  "type": "service_account",
  "project_id": "original-folio-378909",
  "private_key_id": "f6478f27617b15de39fbd1d2c03cf8e8b37c9bcf",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDz13kiAOrgFdjj\nSl1e9yvyJRD30Aq2L8q52mEVq/4QdAjCIop/B72DxriI7oI5IDzrBdCuTXf/HaPl\niErtP4d8JlAGRhURA9RSE2goGJR+GLJBl046/is26luPh+E9rHVHmCpyslkZkhM1\nnnXw/mYKDNAJsYnlbnrmIpC+QfVzqRGadRQ+f5CAVJJQ7ov4mj0XibIG6W8mqkUj\nXu3h4PZKY3Y8f/rNPA4v6FDIvyWN+T9Mqx/rwozOR952p8/+T7n7puuHW5AaPgwT\nn4nvv5nZRTKpiIc5bLZCRajaqNHl6xM0LYoVJC4RMJ+BPOtkjlBjnBnkgqq3lUdm\nhNidZLgxAgMBAAECggEABSYVFK8nIBTVNxgEw8EaTGy0yiP6ax/akV65HlMOHfss\nDKv1sSQHRmGTSuPmlZRDgqIFRr4gxQvZwDp6CSUTMRKuunH8I6QpSKB7hzfQQEXf\nLLQ7adKgWoXFQ2qtRA2KTlKgmDp0saEnnSIaKWNFYXV+2cRZJ68T2TYC/A6qb/cO\neFM3mKO6X0jO1O1aj3z6Whwc0uYD8m82zdYjeLDGLM4krN7gXc+ximOcSL++IlRM\nJAgGp2c7Upxzz/lQBmpfrNkc9gOyHyQ36RsWr+Zya4ncll+UDDB/xtqmBhSxoFfy\nXMPrAidlKCdtAgORP97zoR3aBtJf87dKrmUJfyYbKQKBgQD9ahEEvWxhLJJ49r9m\nP7nZr4QlZKpFzE78uDd9QM0AJOuWQqJxzG4BWZC3eneCuDBnBvbQcDcKuUkuaMWB\ne1x+1tX60S826j0UlmXHq4mNys45cVIXFq3W/PTuk1WJu1di8Yb+pW+LCjczb/uR\nLbLR2aLPQJvRBHTpmJRcoTzkOQKBgQD2VGcEO28UJjFvWrbOXCn+q3taLKqNOhUN\nRpYuShgpolc9qMgvQC6he8qz5s/jPKK6RSVxJD1NMYMCidW+6eGbfoDwDxzaYXpP\nEy/ajI5g0tu3etz+ct4IDowz7iCBE9wlJ/kulDWAgxXv1OVquiqQxXsUj+A2xHwV\nJCEqzrAjuQKBgQDxOvCsZG0xK67a+3hDq1INiOjwd50nCFAAfpRD5VXAV2T0CsZ8\nMbBeFJaQMkJl61QYHycAUHH1AWBKj23DzlzEWVokgtDBI8W1PV3x7rbohTA+ukL8\nu5gMWYwHN7VrgSy0gVqSOYWvA7B8hJMjJi9dWCGFzOkG1Yk9fQNuEgbW8QKBgQC/\n02KV7SLHcia1LNOHSEZ7yFa7FmWKrVyPhhSV36WJZp7BqZqbEUQ/BQQJrQjfUOz4\nWbiarzn9zzzS0Tve/ItwZ8dJKruxZI+23J47d5G43Pu1mrxWemVlqM6N8jblze12\nEfb+yvQPLAX9SrGNt4RGUUNT8+cLP1/Rpt0dVO/eIQKBgQC9xIcSDgfTsUTBDPhG\nfzftkIPNrrLNum5LkNkIR3b1P+nq9+b/21QmoM1Ua8sjyv4495w/sV42QHGppN0T\nE90ugxqhzqfaCrRmUQvjx/hwyY95GmHX5tEEY7PB29MDtLfx9CNvv5AYNafkv9xz\nVbxCNBO/znvJt2TjmOmuBkoALw==\n-----END PRIVATE KEY-----\n",
  "client_email": "google-sheets-admin@original-folio-378909.iam.gserviceaccount.com",
  "client_id": "110843973192275836473",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/google-sheets-admin%40original-folio-378909.iam.gserviceaccount.com"
}'''

st.write(creds_file)

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
                gdb.update_google_sheets_db(row_to_add, current_date, creds_file)
            
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
    google_sheets_df = gdb.read_google_sheets_db(creds_file)

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