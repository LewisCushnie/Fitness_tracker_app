import pygsheets
from datetime import date
import pandas as pd
import streamlit as st
import tempfile
import json

def _google_creds_as_file():

    # get all secrets from streamlit
    _type = st.secrets["_type"]
    project_id = st.secrets["project_id"]
    private_key_id = st.secrets["private_key_id"]
    private_key = st.secrets["private_key"]
    client_email = st.secrets["client_email"]
    client_id = st.secrets["client_id"]
    auth_uri = st.secrets["auth_uri"]
    token_uri = st.secrets["token_uri"]
    auth_provider_x509_cert_url = st.secrets["auth_provider_x509_cert_url"]
    client_x509_cert_url = st.secrets["client_x509_cert_url"]

    # temp = tempfile.NamedTemporaryFile()
    # temp.write(json.dumps({
    #     "type": _type,
    #     "project_id": project_id,
    #     "private_key_id": private_key_id,
    #     "private_key": private_key,
    #     "client_email": client_email,
    #     "client_id": client_id,
    #     "auth_uri": auth_uri,
    #     "token_uri": token_uri,
    #     "auth_provider_x509_cert_url": auth_provider_x509_cert_url,
    #     "client_x509_cert_url": client_x509_cert_url
    # }))
    # temp.flush()

    # config = {
    #     "type": _type,
    #     "project_id": project_id,
    #     "private_key_id": private_key_id,
    #     "private_key": private_key,
    #     "client_email": client_email,
    #     "client_id": client_id,
    #     "auth_uri": auth_uri,
    #     "token_uri": token_uri,
    #     "auth_provider_x509_cert_url": auth_provider_x509_cert_url,
    #     "client_x509_cert_url": client_x509_cert_url
    # }
    config = f'''{{
        "type": "{_type}",
        "project_id": "{project_id}",
        "private_key_id": "{private_key_id}",
        "private_key": "{private_key}",
        "client_email": "{client_email}",
        "client_id": "{client_id}",
        "auth_uri": "{auth_uri}",
        "token_uri": "{token_uri}",
        "auth_provider_x509_cert_url": "{auth_provider_x509_cert_url}",
        "client_x509_cert_url": "{client_x509_cert_url}"
    }}'''

    tfile = tempfile.NamedTemporaryFile(mode="w+")
    json.dump(config, tfile).encode('utf8')
    # a = a.encode('utf-8')
    tfile.flush()
    config = tfile.name
    
    # .encode('utf-8')
    
    # return tfile
    return config

def read_google_sheets_db(creds_file):
    # https://medium.com/game-of-data/play-with-google-spreadsheets-with-python-301dd4ee36eb
    #authorization

    # gc = pygsheets.authorize(service_file='original-folio-378909-f6478f27617b.json')
    # gc = pygsheets.authorize(service_file= creds_file)
    gc = pygsheets.authorize(client_secret='client_secret.json', service_account_json= creds_file)

    #open the google spreadsheet (where 'PY to Gsheet Test' is the name of my sheet)
    sh = gc.open('Fitness_App_db')

    #select the first sheet 
    wks = sh[0]

    # output as df
    google_sheets_df = wks.get_as_df()

    return google_sheets_df

def update_google_sheets_db(row_to_add, date_choice, creds_file):
    # https://medium.com/game-of-data/play-with-google-spreadsheets-with-python-301dd4ee36eb
    #authorization

    # gc = pygsheets.authorize(service_file='original-folio-378909-f6478f27617b.json')
    # gc = pygsheets.authorize(service_file= creds_file)
    gc = pygsheets.authorize(client_secret='client_secret.json', service_account_json= creds_file)

    #open the google spreadsheet (where 'PY to Gsheet Test' is the name of my sheet)
    sh = gc.open('Fitness_App_db')

    #select the first sheet
    wks = sh[0]

    # create dataframe from sheet
    df = wks.get_as_df()

    # convert date column to date
    df['Date'] = pd.to_datetime(df['Date'])
    df['Date'] = df['Date'].dt.date

    # find index of current date in dataframe
    df_row = df.index[df['Date'] == date_choice][0]

    # add 2 because of index starting from 0 in pandas, and headings row
    wks_row = df_row + 2

    # weight cell to change
    weight_cell = f'B{wks_row}'

    # update the row for the current date with the inputted values
    wks.update_row(wks_row, row_to_add, col_offset= 1)