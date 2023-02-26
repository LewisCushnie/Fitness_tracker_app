import pygsheets
from datetime import date
import pandas as pd
import streamlit as st

def read_google_sheets_db():
    # https://medium.com/game-of-data/play-with-google-spreadsheets-with-python-301dd4ee36eb
    #authorization
    gc = pygsheets.authorize(service_file='original-folio-378909-f6478f27617b.json')

    #open the google spreadsheet (where 'PY to Gsheet Test' is the name of my sheet)
    sh = gc.open('Fitness_App_db')

    #select the first sheet 
    wks = sh[0]

    # output as df
    google_sheets_df = wks.get_as_df()

    return google_sheets_df


def update_google_sheets_db(row_to_add, date_choice):
    # https://medium.com/game-of-data/play-with-google-spreadsheets-with-python-301dd4ee36eb
    #authorization
    gc = pygsheets.authorize(service_file='original-folio-378909-f6478f27617b.json')

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