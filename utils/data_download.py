import requests
import json
import pandas as pd
from pandas.io.json import json_normalize
from os.path import exists
from datetime import date
import os
import time
import json
import numpy as np
from sklearn.neighbors import BallTree
from sklearn.metrics import DistanceMetric
from datetime import datetime, timedelta

def get_strava_refresh_token(CLIENT_ID, CLIENT_SECRET, STRAVA_REFRESH_TOKEN):

    '''
    This function reads the strava access token from the json file
    in utils/access_tokens. If it has not expired, the function returns
    the access token and leaves the json file in place. Otherwise, the
    function requests a refresh token and updates the json file with
    the new token.
    '''

    # Get the tokens from file to connect to Strava
    # with open('utils/access_tokens/strava_tokens.json') as json_file:
    #     strava_tokens = json.load(json_file)

    # If access_token has expired then use the refresh_token to get the new access_token
    if STRAVA_REFRESH_TOKEN < time.time():
        print('Generating refresh access token...')

    # Make Strava auth API call with current refresh token
        response = requests.post(
                            url = 'https://www.strava.com/oauth/token',
                            data = {
                                    'client_id': CLIENT_ID,
                                    'client_secret': CLIENT_SECRET,
                                    'grant_type': 'refresh_token',
                                    'refresh_token': STRAVA_REFRESH_TOKEN
                                    }
                        )

    # Save response as json in new variable
        new_strava_tokens = response.json()

    # # Save new tokens to file
    #     with open('utils/access_tokens/strava_tokens.json', 'w') as outfile:
    #         json.dump(new_strava_tokens, outfile)

    # else:
    #     print('Access token has not expired yet...')

    return new_strava_tokens

def get_strava_tokens(CLIENT_ID, CLIENT_SECRET, code, reset):
    '''
    http://www.strava.com/oauth/authorize?client_id=98967&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=profile:read_all,activity:read_all
    
    '''

    # Make Strava auth API call with your 
    # client_code, client_secret and code
    if reset:
        response = requests.post(
                            url = 'https://www.strava.com/oauth/token',
                            data = {
                                    'client_id': CLIENT_ID,
                                    'client_secret': CLIENT_SECRET,
                                    # code changes each time
                                    'code': code,
                                    'grant_type': 'authorization_code'
                                    }
                        )

        #Save json response as a variable
        strava_tokens = response.json()

        # Save tokens to file
        with open('utils/access_tokens/strava_tokens.json', 'w') as outfile:
            json.dump(strava_tokens, outfile)

def get_maps_data():
    google_maps_df = pd.read_json('google_maps/Saved Places.json')

    # load data using Python JSON module
    with open('google_maps/Saved Places.json','r') as f:
        data = json.loads(f.read())

    # Flatten data
    google_maps_df = pd.json_normalize(data, record_path =['features'])

    # get necessary columns
    google_maps_df = google_maps_df[['properties.Title', 'geometry.coordinates']]

    return google_maps_df

def get_key_locations():

    data = {
    "Location": ["Tokei Martial Arts"
                ,"Home"
                ,"Office"],
    "Lat": [51.5035157, 51.4723345, 51.514418899999995],                
    "Long": [-0.0814162, -0.0421276, -0.0830479]
    }

    #load data into a DataFrame object:
    maps_data = pd.DataFrame(data)

    return maps_data

def clean_and_enrich_strava_data(activities, current_date):

    # split the latlng column into seperate lat and long columns
    activities[['start_lat','start_long']] = pd.DataFrame(activities['start_latlng'].tolist()
                                                            , index= activities.index)

    activities[['end_lat','end_long']] = pd.DataFrame(activities['end_latlng'].tolist()
                                                            , index= activities.index)

    # get maps locations
    maps_data = get_key_locations()
    
    # find matching locations in key locations from maps_data
    # create Balltree model
    coords = np.radians(maps_data[['Lat', 'Long']])
    dist = DistanceMetric.get_metric('haversine')
    tree = BallTree(coords, metric=dist)

    # find matching start locations
    coords = np.radians(activities[['start_lat', 'start_long']])
    distances, indices = tree.query(coords, k=1)

    # create new columns 
    activities['start_location'] = maps_data['Location'].iloc[indices.flatten()].values
    activities['start_distance_diff'] = distances.flatten()

    # find matching end locations
    coords = np.radians(activities[['end_lat', 'end_long']])
    distances, indices = tree.query(coords, k=1)

    # create new columns 
    activities['end_location'] = maps_data['Location'].iloc[indices.flatten()].values
    activities['end_distance_diff'] = distances.flatten()

    # find locations where distance diff to high -> label as 'other'
    max_diff = 0.0099
    error_too_high_mask = activities['start_distance_diff'] > max_diff
    error_too_high_mask = activities['end_distance_diff'] > max_diff
    activities['start_location'][error_too_high_mask] = 'Other'
    activities['end_location'][error_too_high_mask] = 'Other'

    # convert the 'Date' column to datetime format
    activities['start_date_local']= pd.to_datetime(activities['start_date_local']).dt.date

    # convert distance from m -> km
    activities['distance'] = activities['distance'].div(1000)
    # convert time from s -> min
    activities['moving_time'] = activities['moving_time'].div(60)
    activities['elapsed_time'] = activities['elapsed_time'].div(60)

    # fill in for missing dates by creating date range from date(min) -> date(max), then left joining
    range = pd.date_range(start= activities['start_date_local'].min(), end= current_date, freq="D")
    date_df = pd.DataFrame(range, columns=['date'])
    date_df['date']= pd.to_datetime(date_df['date']).dt.date

    # left join to date range in order to add dates with no activities
    activities = pd.merge(date_df, activities, how='left', left_on='date', right_on= 'start_date_local')

    # replace certain columns N/A for 0 for aggregration and graphing
    fill_na_with_zero = ['distance'
                        ,'moving_time'
                        ,'elapsed_time'
                        ,'total_elevation_gain'
                        ,'average_speed'
                        ,'max_speed'
                        ,'elev_high'
                        ,'elev_low']

    activities[fill_na_with_zero] = activities[fill_na_with_zero].fillna(0)
    activities['type'] = activities['type'].fillna('null')

    # rename columns
    activities.rename(columns = {'distance':'distance (km)'
                                ,'moving_time': 'moving time (min)'
                                ,'elapsed_time': 'elapsed time (min)'
                                ,'total_elevation_gain': 'total elevation gain (m)'
                                ,'average_speed': 'average speed (m/s)'
                                ,'max_speed': 'max speed (m/s)'
                                ,'elev_high': 'elev high (m)'
                                ,'elev_low': 'elev low (m)'}, inplace = True)

    # add emoji columns to dataframe
    count_tokei_start = activities['start_location'].str.count("Tokei").sum()
    count_tokei_end = activities['end_location'].str.count("Tokei").sum()

    # select the gym count from the column with the highest count
    if count_tokei_end > count_tokei_start:
        selected_gym_column = 'end_location'

    elif count_tokei_start > count_tokei_end:
        selected_gym_column = 'start_location'

    else:
        # if equal, it doesnt matter which column is selected
        selected_gym_column = 'start_location'

    gym_mask = (activities[selected_gym_column] == 'Tokei Martial Arts')
    ride_mask = (activities['type'] == 'Ride')
    run_mask = (activities['type'] == 'Run')

    # add columns to count runs
    activities.loc[gym_mask, 'tokei_count'] = 1
    activities['tokei_count'] = activities['tokei_count'].fillna(0)

    # add columns to count runs
    activities.loc[ride_mask, 'ride_count'] = 1
    activities['ride_count'] = activities['ride_count'].fillna(0)

    # add columns to count runs
    activities.loc[run_mask, 'run_count'] = 1
    activities['run_count'] = activities['run_count'].fillna(0)

    # add columns to count runs
    activities.loc[run_mask, 'run'] = '🏃'
    activities['run'] = activities['run'].fillna('❌')

    # add columns to count gym
    activities.loc[gym_mask, 'tokei'] = '🏋️'
    activities['tokei'] = activities['tokei'].fillna('❌')

    # add columns to count cycle
    activities.loc[ride_mask, 'ride'] = '🚴'
    activities['ride'] = activities['ride'].fillna('❌')

    # add cumulative distance column
    activities['cumulative_distance'] = activities['distance (km)'].cumsum()
    
    return activities

def get_strava_data(current_date):

    '''
    This function scrapes wikipedia to return a list of S&P 500 tickers
    '''

    # files to keep
    file_name = f'strava_activity_data_{current_date}.pkl'
    strava_data_file = f"utils/pickled_activity_data/strava_activity_data_{current_date}.pkl"
    gitkeep_file = '.gitkeep'

    # (1) delete old files in the pickle directories
    directory_path = 'utils/pickled_activity_data'

    # itterate through files in the target directory and delete old files
    for file in os.listdir(directory_path):

        # do not delete files if they are today's file, or the .gitkeep file
        if file in [file_name, gitkeep_file]: 
            pass
        
        # delete any other files present in the directory
        else:
            file_path = f'{directory_path}/{file}'
            
            try:
                os.remove(file_path)
                print(f'deleting: {file}...')

            except:
                raise Exception

    # (2) check if the up-to-date pickle file already exists
    file_exists = exists(strava_data_file)

    # (3) if the file does not already exist, create dataframe and pickle it 
    if not file_exists:

        # Get the tokens from file to connect to Strava
        with open('utils/access_tokens/strava_tokens.json') as json_file:
            strava_tokens = json.load(json_file)

        # Loop through all activities
        page = 1
        url = "https://www.strava.com/api/v3/activities"
        access_token = strava_tokens['access_token']

        # Create dataframe for desired data fields
        activities = pd.DataFrame(
            columns = [
                    "id"
                    ,"name"
                    ,"start_date_local"
                    ,"type"
                    ,"distance"
                    ,"moving_time"
                    ,"elapsed_time"
                    ,"total_elevation_gain"
                    ,"start_latlng"
                    ,"end_latlng"
                    ,"timezone"
                    ,"average_speed"
                    ,"max_speed"
                    ,"elev_high"
                    ,"elev_low"
            ]
        )

        # get data from strava to populate dataframe
        while True:
            
            # get page of activities from Strava
            page_url = f'{url}?access_token={access_token}&per_page=200&page={str(page)}'
            r = requests.get(page_url)
            r = r.json()
            
            # if no results then exit loop
            if (not r):
                break
            
            # otherwise add new data to dataframe
            for x in range(len(r)):
                activities.loc[x + (page-1)*200,'id'] = r[x]['id']
                activities.loc[x + (page-1)*200,'name'] = r[x]['name']
                activities.loc[x + (page-1)*200,'start_date_local'] = r[x]['start_date_local']
                activities.loc[x + (page-1)*200,'type'] = r[x]['type']
                activities.loc[x + (page-1)*200,'distance'] = r[x]['distance']
                activities.loc[x + (page-1)*200,'moving_time'] = r[x]['moving_time']
                activities.loc[x + (page-1)*200,'elapsed_time'] = r[x]['elapsed_time']
                activities.loc[x + (page-1)*200,'total_elevation_gain'] = r[x]['total_elevation_gain']
                activities.loc[x + (page-1)*200,'start_latlng'] = r[x]['start_latlng']
                activities.loc[x + (page-1)*200,'end_latlng'] = r[x]['end_latlng']
                activities.loc[x + (page-1)*200,'timezone'] = r[x]['timezone']
                activities.loc[x + (page-1)*200,'average_speed'] = r[x]['average_speed']
                activities.loc[x + (page-1)*200,'max_speed'] = r[x]['max_speed']
                activities.loc[x + (page-1)*200,'elev_high'] = r[x]['elev_high']
                activities.loc[x + (page-1)*200,'elev_low'] = r[x]['elev_low']

            # increment page
            page += 1

        # apply cleaning and transforms to df
        activities = clean_and_enrich_strava_data(activities, current_date)

        # pickle the new dataframe
        activities.to_pickle(strava_data_file) 

        print(f'creating strava_activity_data_{current_date}.pkl file...')

            # ------------------------
            # TRANSFORMATIONS:
            # ------------------------

            # # split the latlng column into seperate lat and long columns
            # activities[['start_lat','start_long']] = pd.DataFrame(activities['start_latlng'].tolist()
            #                                                         , index= activities.index)

            # activities[['end_lat','end_long']] = pd.DataFrame(activities['end_latlng'].tolist()
            #                                                         , index= activities.index)

    # (4) if the file already exists, return the data from the pickle file
    else:

        # get the data from the pickle file
        activities = pd.read_pickle(strava_data_file)

        print(f'Loading strava_activity_data_{current_date}.pkl file...')

    return activities