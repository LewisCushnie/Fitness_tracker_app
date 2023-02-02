import requests
import json
import pandas as pd
from pandas.io.json import json_normalize
from os.path import exists
from datetime import date
import os
import time
import csv
import utils.data_download as dd
import utils.env_variables as ev

def main():

    # get current date
    current_date = date.today()

    # get the client id and secret required for the api access token
    CLIENT_ID, CLIENT_SECRET = ev.get_secrets()

    # get strava refresh token if old one has expired
    dd.get_strava_refresh_token(CLIENT_ID, CLIENT_SECRET)

    # get strava data from the api
    activities = dd.get_strava_data(current_date)

    print(activities)

if __name__ == '__main__':
    main()