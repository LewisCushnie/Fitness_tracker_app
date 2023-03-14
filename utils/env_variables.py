import os
import logging

def get_secrets():

    # if running locally, get login credentials from .env file
    current_user = os.environ['USER']
    print(f'current user is: {current_user}')

    # if running locally from lewiscushnie's computer, get nv variables from .env
    if current_user == 'lewiscushnie':
        print('get secrets from local .env file')
        from dotenv import load_dotenv
        load_dotenv()

        CLIENT_ID = os.getenv('CLIENT_ID')
        CLIENT_SECRET = os.getenv('CLIENT_SECRET')
        STRAVA_REFRESH_TOKEN = os.getenv('STRAVA_REFRESH_TOKEN')

        logging.info(f'Environment variables successfully collected')

    # if running on a (github) virtual machine, get env variables from github secrets
    else:
        try:
            # get the email login credentials from github secrets
            print('get secrets from github secrets')
            CLIENT_ID = os.environ['CLIENT_ID']
            CLIENT_SECRET = os.environ['CLIENT_SECRET']
            STRAVA_REFRESH_TOKEN = os.environ['STRAVA_REFRESH_TOKEN']

            logging.info(f'Environment variables successfully collected')

        except KeyError:
            logging.info(f'Could not collect environment variables')

    return CLIENT_ID, CLIENT_SECRET, STRAVA_REFRESH_TOKEN