import streamlit as st
import utils.data_download as dd
import utils.google_sheets_db as gdb
import utils.streamlit_modules as sm
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime, timedelta, date
import gspread

# set page config options
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

# get strava api information from secrets to refresh strava data
CLIENT_ID = st.secrets["CLIENT_ID"]
CLIENT_SECRET = st.secrets["CLIENT_SECRET"]
STRAVA_REFRESH_TOKEN = st.secrets["STRAVA_REFRESH_TOKEN"]
strava_tokens = dd.get_strava_refresh_token(CLIENT_ID, CLIENT_SECRET, STRAVA_REFRESH_TOKEN)

# get current date
current_date = date.today()

# ====================== PAGE STARTS =============================
st.title('Fitness Stats 🏃 🏋️ 🚴')
st.info("You can't improve what you can't measure...")
st.info('''Current Objectives:
- Eat breakfast every day
- Gym Mondays, Wednesdays, Saturdays
- Stretch every day in the morning
        ''')

# ================================================================
# ================= GET DATA AND SET CONTEXT =====================
# ================================================================

# get strava data from the api
strava_activities_df = dd.get_strava_data(current_date, strava_tokens)

# apply cleaning and transforms to df
strava_activities_df = dd.clean_and_enrich_strava_data(strava_activities_df, current_date)

# read data from the google sheets 'database'
google_sheets_df, worksheet = gdb.get_google_sheets_as_df()

# get maps locations
maps_data = dd.get_key_locations()

# create tabs for the app
tab1, tab2, tab3, tab4 = st.tabs(['Daily Form', 'Cardio Analysis - Time Period', 'Cardio Analysis - This Year', 'Physical Tracking'])

# ================================================================
# ===================== SET GLOBAL VARIABLES =====================
# ================================================================ 

# DAILY FORM
with tab1:

    df = pd.DataFrame(
    [
       {"command": "st.selectbox", "rating": 4, "is_widget": True},
       {"command": "st.balloons", "rating": 5, "is_widget": False},
       {"command": "st.time_input", "rating": 3, "is_widget": True},
   ]
    )
    edited_df = st.experimental_data_editor(df, num_rows="dynamic")

    favorite_command = edited_df.loc[edited_df["rating"].idxmax()]["command"]
    st.markdown(f"Your favorite command is **{favorite_command}** 🎈")

    def weight_form():
        with st.form(key= 'daily form'):

            integers = range(41)
            situp_integers = range(0, 1000, 25)
            presup_integers = range(0, 1000, 25)

            weight = st.number_input('Enter mass from today (kg):', step= 0.1)
            n_stretched = st.selectbox('How many times did I stretch:', integers)

            n_situps = st.selectbox('Sit up reps:', situp_integers, )
            n_press_ups = st.selectbox('Press up reps:', presup_integers)

            w_pullup = st.number_input('Pull up additional weight (kg):', step = 1)
            r_pullup = st.selectbox('Pullup reps:', integers, key= 'r_pullup')
            
            w_bench = st.number_input('Bench press (kg):', step = 1)
            r_bench = st.selectbox('Bench reps:', integers, key= 'r_bench')

            # Every form must have a submit button.
            submitted = st.form_submit_button("Submit")
            row_to_add = [current_date
                        ,n_stretched
                        ,weight
                        ,w_pullup
                        ,r_pullup
                        ,w_bench
                        ,r_bench]
            
            if submitted:

                # create a copy of the existing google sheets df
                google_sheets_df_row_add = google_sheets_df.copy()

                # convert date column to date so correct row index can be found
                google_sheets_df_row_add['Date'] = pd.to_datetime(google_sheets_df_row_add['Date'])
                google_sheets_df_row_add['Date'] = google_sheets_df_row_add['Date'].dt.date

                # find index of current date in dataframe
                df_row = google_sheets_df_row_add.index[google_sheets_df_row_add['Date'] == current_date][0]

                # add data from the form submission to the dataframe
                google_sheets_df_row_add.iloc[df_row] = row_to_add

                # convert datetime back to string before pushing to database
                google_sheets_df_row_add['Date'] = pd.to_datetime(google_sheets_df_row_add['Date'])
                google_sheets_df_row_add['Date'] = google_sheets_df_row_add['Date'].dt.strftime('%Y-%m-%d')

                # push the changes to the google sheets database
                worksheet.update([google_sheets_df_row_add.columns.values.tolist()] + google_sheets_df_row_add.values.tolist())

                st.success("Submitted!")
            
            else:
                pass
        
        return weight, n_stretched, submitted

    # weight form to collect weight data
    weight = weight_form()

# CARIDO ANALYSIS - TIME PERIOD
with tab2:

    line = '---'
    st.header('Set Global Variables')

    strava_by_daterange_df = strava_activities_df.copy()

    # select start and end date range for app widgets
    col1, col2 = st.columns(2)
    with col1:
        d = timedelta(days = 10)
        global_start = st.date_input('Start of timeframe', value = current_date - d)

    with col2:
        global_end = st.date_input('End of timeframe', value= current_date)

    # filter for selected date range
    mask = (strava_by_daterange_df['date'] >= global_start) & (strava_by_daterange_df['date'] <= global_end)
    strava_by_daterange_df = strava_by_daterange_df.loc[mask]
    
    # find the day diff
    day_diff = (global_end - global_start).days

    # display summary stats
    sm.show_cardio_summary_stats(strava_by_daterange_df, day_diff)

    # ----------------------------------------------------------------
    # ----------------------- COUNTER --------------------------------
    # ----------------------------------------------------------------
    st.write(line)
    st.header('Activity Tracker')

    # group the activities dataframe to get a day-by-day count
    activities_by_date = strava_by_daterange_df.groupby("date")[["ride_count", "run_count", "tokei_count"]].sum()

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

    chart = alt.Chart(strava_by_daterange_df).mark_bar().encode(
        x='date:O',
        y='distance (km):Q',
        color='type:N'
    )
    st.altair_chart(chart, use_container_width= True, theme= 'streamlit')

# CARIDO ANALYSIS - THIS YEAR
with tab3:

    # get first day of current year
    current_year = current_date.year
    first_day_of_year = date(current_year, 1, 1)

    # copy the strava dataframe and filter for only current-year dates
    strava_this_year_df = strava_activities_df.copy()

    # filter for selected date range
    mask = (strava_this_year_df['date'] >= first_day_of_year) & (strava_this_year_df['date'] <= current_date)
    strava_this_year_df = strava_this_year_df.loc[mask]
    
    # find the day diff
    day_diff = (current_date - first_day_of_year).days
    
    # display summary stats
    sm.show_cardio_summary_stats(strava_this_year_df, day_diff)

    # get required data and pivot it for altair
    alt_data = strava_this_year_df[['date', 'cumulative distance riden (km)', 'cumulative distance run (km)']]
    alt_data = alt_data.melt('date', var_name= 'Type', value_name= 'Distance (km)')

    st.header('Cumulative distances for this year')
    rides = alt.Chart(alt_data).mark_line(
    ).encode(
        alt.X('date:T', axis=alt.Axis(format="%B")),
        y='Distance (km):Q',
        color= 'Type:N'
    ).configure_legend(orient='bottom', columnPadding= 30, labelLimit= 1000)

    st.altair_chart(rides, use_container_width= True, theme= 'streamlit')

# PHYSICAL TRACKING
with tab4:
    # ----------------------------------------------------------------
    # ------------------- PHYSICAL TRACKING --------------------------
    # ----------------------------------------------------------------


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

    # === MASS CALCS =====
    # dataframe that contains only non-null mass and date data
    non_null_mass = google_sheets_df.loc[google_sheets_df['Mass (kg)'].notnull(), ['Date', 'Mass (kg)']]

    # get my most recent mass recording
    current_mass = non_null_mass.iloc[len(non_null_mass)-1]['Mass (kg)']
    starting_mass = non_null_mass['Mass (kg)'].iloc[0]
    perc_diff = round(((current_mass-starting_mass)/starting_mass)*100, 1)

    # === RUN CALCS =====
    # find all runs
    runs = strava_activities_df.loc[strava_activities_df['type'] == 'Run']

    # find all 5K runs within specified allowable range
    five_k_runs = runs.loc[runs['distance (km)'] >= 5]
    five_k_runs = five_k_runs.loc[five_k_runs['distance (km)'] <= 5.2]

    # find distance exceeding 5K
    five_k_runs['extra distance (m)'] = (five_k_runs['distance (km)'] - 5)*1000

    # find expected extra time (from the average speed)
    five_k_runs['extra time (s)'] = (five_k_runs['extra distance (m)'])/(five_k_runs['average speed (m/s)'])

    # find expected exact 5k time
    five_k_runs['5k time (s)'] = (five_k_runs['moving time (min)']*60) - (five_k_runs['extra time (s)'])

    def convert_to_preferred_format(sec):
        sec = sec % (24 * 3600)
        sec %= 3600
        min = sec // 60
        sec %= 60
        return "%02d:%02d" % (min, sec) 

    # expected time corrected for overrun and standing time
    five_k_runs['5k time (mins)'] = five_k_runs['5k time (s)'].apply(convert_to_preferred_format)

    # get pace per km
    five_k_runs['Pace (mins/km)'] = ((five_k_runs['moving time (min)'])/(five_k_runs['distance (km)'])*60).apply(convert_to_preferred_format)

    # get only the data I care about
    five_k_runs_key_data = five_k_runs[['date', '5k time (mins)', 'Pace (mins/km)']]

    # manually add some older times from run tracker app for context
    run_tracker_5ks = pd.DataFrame(np.array(
        [['2022-09-08', '28:10', '05:37'], 
        ['2022-08-27', '26:09', '05:13'], 
        ['2022-08-23', '24:15', '04:49'], 
        ['2022-08-19', '24:28', '04:53'], 
        ['2022-08-15', '24:39', '04:54']
        ]),
        columns=['date', '5k time (mins)', 'Pace (mins/km)'])

    # union the two dataframes
    five_k_runs_key_data = pd.concat([five_k_runs_key_data, run_tracker_5ks])
    # five_k_runs_key_data.sort_values(by='date', inplace = True) 
    five_k_runs_key_data['date']= pd.to_datetime(five_k_runs_key_data['date'])
    five_k_runs_key_data.sort_values(by='date', inplace = True) 
    starting_five_k_time = five_k_runs_key_data.iloc[0]['5k time (mins)']
    best_five_k_time = five_k_runs_key_data['5k time (mins)'].min()


    # ======================= PLOTTING ============================

    target_mass = 76
    target_time = '21:00'

    non_null_mass['Target Mass (kg)'] = target_mass
    five_k_runs_key_data['Target 5k time (mins)'] = target_time

    st.header('Physical Tracking')
    col1, col2 = st.columns(2)
    with col1:
        st.metric('Current mass (kg)'
            ,current_mass
            ,f'{perc_diff}%')
        
    with col2:
        st.metric('Best 5K time (mins-secs)'
            ,best_five_k_time
            ,starting_five_k_time)

    st.header('Mass Tracking')
    mass_chart = alt.Chart(non_null_mass).transform_fold(
        ['Mass (kg)', 'Target Mass (kg)']
    ).mark_line().encode(
    x = alt.X('Date:O'),
    y = alt.Y('value:Q', scale=alt.Scale(domain=[google_sheets_df['Mass (kg)'].min(), target_mass + 1])),
    color = 'key:N'
    )
    st.altair_chart(mass_chart, use_container_width= True, theme= 'streamlit')
    
    st.header('5K Time Tracking')
    five_k_chart = alt.Chart(five_k_runs_key_data).transform_fold(
        ['5k time (mins)', 'Target 5k time (mins)']
    ).mark_line().encode(
    x = alt.X('date:O'),
    y = alt.Y('value:O', sort= 'descending'),
    color = 'key:N'
    )
    st.altair_chart(five_k_chart, use_container_width= True, theme= 'streamlit')
