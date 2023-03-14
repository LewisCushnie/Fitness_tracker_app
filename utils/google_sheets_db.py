from datetime import date
import pandas as pd
import streamlit as st
import tempfile
import json
import gspread

def get_google_sheets_as_df():

    '''
    This function connects with the google sheets
    database used to store personal records. It returns
    a dataframe containing all the data in the sheet
    '''

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

    # build the credentials dict using the streamlit secrets
    my_credentials = {
    "type": _type,
    "project_id": project_id,
    "private_key_id": private_key_id,
    "private_key": private_key,
    "client_email": client_email,
    "client_id": client_id,
    "auth_uri": auth_uri,
    "token_uri": token_uri,
    "auth_provider_x509_cert_url": auth_provider_x509_cert_url,
    "client_x509_cert_url": client_x509_cert_url
    }

    # authenticate
    gc = gspread.service_account_from_dict(my_credentials)

    # open the required google sheet
    sh = gc.open('Fitness_App_db')

    # open the required worksheet in the google sheet
    ws = sh.worksheet("Records")

    # convert the worksheet to a pandas df
    google_sheets_df = pd.DataFrame(ws.get_all_records())

    return google_sheets_df

def update_google_sheets_db(row_to_add, date_choice, creds_file):
    # https://medium.com/game-of-data/play-with-google-spreadsheets-with-python-301dd4ee36eb
    #authorization

    # gc = pygsheets.authorize(service_file='original-folio-378909-f6478f27617b.json')
    # gc = pygsheets.authorize(service_file= creds_file)
    # gc = pygsheets.authorize(service_file=creds_file)

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