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
    worksheet = sh.worksheet("Records")

    # convert the worksheet to a pandas df
    google_sheets_df = pd.DataFrame(worksheet.get_all_records())

    return google_sheets_df, worksheet

def update_google_sheets_db_2(google_sheets_df, worksheet):

    worksheet.update([google_sheets_df.columns.values.tolist()] + google_sheets_df.values.tolist())