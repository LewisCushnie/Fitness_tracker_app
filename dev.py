import json
import gspread
import pandas as pd
from datetime import date


# SCOPES = ('https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive')
# service_account_info = json.loads(secret_dict)
# my_credentials = service_account.Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
# gc = pygsheets.authorize(custom_credentials=my_credentials)

my_credentials = {
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
}

gc = gspread.service_account_from_dict(my_credentials)

sh = gc.open('Fitness_App_db')

ws = sh.worksheet("Records")

df = pd.DataFrame(ws.get_all_records())

current_date = date.today()

# get index of current date in dataframe
current_date_index = df[df['Date']== f'{current_date}'].index.values

# use list to add latest row to the dataframe
df.loc[current_date_index] = ['Test', 'Test', 'Test', 'Test', 'Test', 'Test', 'Test']

# overwrite the sheet with the updated df (split into columns + values)
ws.update([df.columns.values.tolist()] + df.values.tolist())

print(df)


# gc = pygsheets.authorize(custom_credentials=my_credentials)

# print('complete')

# sh = gc.open("pygsheetTest")


# #open the google spreadsheet (where 'PY to Gsheet Test' is the name of my sheet)
# sh = gc.open('Fitness_App_db')

# #select the first sheet 
# wks = sh[0]

# # output as df
# google_sheets_df = wks.get_as_df()

# print(google_sheets_df)

