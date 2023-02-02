import requests
import json
import pandas as pd
from pandas.io.json import json_normalize
from os.path import exists
from datetime import date
import os
import time

def get_strava_refresh_token(CLIENT_ID, CLIENT_SECRET):

    '''
    This function reads the strava access token from the json file
    in utils/access_tokens. If it has not expired, the function returns
    the access token and leaves the json file in place. Otherwise, the
    function requests a refresh token and updates the json file with
    the new token.
    '''

    # Get the tokens from file to connect to Strava
    with open('utils/access_tokens/strava_tokens.json') as json_file:
        strava_tokens = json.load(json_file)

    # If access_token has expired then use the refresh_token to get the new access_token
    if strava_tokens['expires_at'] < time.time():

        print('Generating refresh access token...')

    # Make Strava auth API call with current refresh token
        response = requests.post(
                            url = 'https://www.strava.com/oauth/token',
                            data = {
                                    'client_id': CLIENT_ID,
                                    'client_secret': CLIENT_SECRET,
                                    'grant_type': 'refresh_token',
                                    'refresh_token': strava_tokens['refresh_token']
                                    }
                        )

    # Save response as json in new variable
        new_strava_tokens = response.json()

    # Save new tokens to file
        with open('utils/access_tokens/strava_tokens.json', 'w') as outfile:
            json.dump(new_strava_tokens, outfile)

    else:
        print('Access token has not expired yet...')

def get_strava_tokens(CLIENT_ID, CLIENT_SECRET):
    '''
    
    '''

    # Make Strava auth API call with your 
    #  client_code, client_secret and code
    first_time = False
    if first_time:
        response = requests.post(
                            url = 'https://www.strava.com/oauth/token',
                            data = {
                                    'client_id': CLIENT_ID,
                                    'client_secret': CLIENT_SECRET,
                                    # code changes each time
                                    'code': 'b2464d8c8b50fa4eeda96a0589deaa10c9a92604',
                                    'grant_type': 'authorization_code'
                                    }
                        )

        #Save json response as a variable
        strava_tokens = response.json()

        # Save tokens to file
        with open('utils/access_tokens/strava_tokens.json', 'w') as outfile:
            json.dump(strava_tokens, outfile)

        # Open JSON file and print the file contents 
        # to check it's worked properly
        with open('utils/access_tokens/strava_tokens.json') as check:
            data = json.load(check)

        print(data)

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
        print(f'creating strava_activity_data_{current_date}.pkl file...')

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

            # pickle the new dataframe
            activities.to_pickle(strava_data_file) 

    # (4) if the file already exists, return the data from the pickle file
    else:
        print(f'Loading strava_activity_data_{current_date}.pkl file...')

        # get the data from the pickle file
        activities = pd.read_pickle(strava_data_file)

    return activities