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
line = '---'
st.markdown(line)

# ================================================================
# ================= GET DATA AND SET CONTEXT =====================
# ================================================================

# get current date
current_date = date.today()

# get strava data from the api
activities = dd.get_strava_data(current_date)

# get maps locations
maps_data = dd.get_key_locations()

# ================================================================
# ========== ADD ADDITIONAL COLUMNS TO ACTIVITIES DF =============
# ================================================================

# # find matching locations in key locations from maps_data
# # create Balltree model
# coords = np.radians(maps_data[['Lat', 'Long']])
# dist = DistanceMetric.get_metric('haversine')
# tree = BallTree(coords, metric=dist)

# # find matching start locations
# coords = np.radians(activities[['start_lat', 'start_long']])
# distances, indices = tree.query(coords, k=1)

# # create new columns 
# activities['start_location'] = maps_data['Location'].iloc[indices.flatten()].values
# activities['start_distance_diff'] = distances.flatten()

# # find matching end locations
# coords = np.radians(activities[['end_lat', 'end_long']])
# distances, indices = tree.query(coords, k=1)

# # create new columns 
# activities['end_location'] = maps_data['Location'].iloc[indices.flatten()].values
# activities['end_distance_diff'] = distances.flatten()

# # find locations where distance diff to high -> label as 'other'
# max_diff = 0.0099
# error_too_high_mask = activities['start_distance_diff'] > max_diff
# error_too_high_mask = activities['end_distance_diff'] > max_diff
# activities['start_location'][error_too_high_mask] = 'Other'
# activities['end_location'][error_too_high_mask] = 'Other'

# # convert the 'Date' column to datetime format
# activities['start_date_local']= pd.to_datetime(activities['start_date_local']).dt.date

# # convert distance from m -> km
# activities['distance'] = activities['distance'].div(1000)
# # convert time from s -> min
# activities['moving_time'] = activities['moving_time'].div(60)
# activities['elapsed_time'] = activities['elapsed_time'].div(60)

# # fill in for missing dates by creating date range from date(min) -> date(max), then left joining
# range = pd.date_range(start= activities['start_date_local'].min(), end= current_date, freq="D")
# date_df = pd.DataFrame(range, columns=['date'])
# date_df['date']= pd.to_datetime(date_df['date']).dt.date

# # left join to date range in order to add dates with no activities
# activities = pd.merge(date_df, activities, how='left', left_on='date', right_on= 'start_date_local')

# # replace certain columns N/A for 0 for aggregration and graphing
# fill_na_with_zero = ['distance'
#                     ,'moving_time'
#                     ,'elapsed_time'
#                     ,'total_elevation_gain'
#                     ,'average_speed'
#                     ,'max_speed'
#                     ,'elev_high'
#                     ,'elev_low']

# activities[fill_na_with_zero] = activities[fill_na_with_zero].fillna(0)
# activities['type'] = activities['type'].fillna('null')

# # rename columns
# activities.rename(columns = {'distance':'distance (km)'
#                             ,'moving_time': 'moving time (min)'
#                             ,'elapsed_time': 'elapsed time (min)'
#                             ,'total_elevation_gain': 'total elevation gain (m)'
#                             ,'average_speed': 'average speed (m/s)'
#                             ,'max_speed': 'max speed (m/s)'
#                             ,'elev_high': 'elev high (m)'
#                             ,'elev_low': 'elev low (m)'}, inplace = True)

# ================================================================
# ===================== SET GLOBAL VARIABLES =====================
# ================================================================    

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

st.write(line)
st.header('Activity')

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
