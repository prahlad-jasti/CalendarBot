from __future__ import print_function
from datetime import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
class calendar_app():
    z = 0

def main():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    events = service.events().list(calendarId='primary', singleEvents = True, orderBy='startTime').execute()
    active = False
    first = True
    next_event = None
    next_start = None
    for event in events['items'][::-1]:
        start = datetime.strptime(event['start']['dateTime'][:-6], "%Y-%m-%dT%H:%M:%S")
        end = datetime.strptime(event['end']['dateTime'][:-6], "%Y-%m-%dT%H:%M:%S")
        if (first and start > datetime.now()):
            next_event = event
            next_start = start
        else:
            first = False
        if (start < datetime.now() and end > datetime.now()):
            print("Active event:",event['summary'])
            end_delta = (end - datetime.now()).total_seconds()
            print("Will end in", seconds_to_dhms(end_delta))
            active = True
        if (end < datetime.now()):
            break
    if not active:
        print("No ongoing events.")
    if next_event is None:
        print("No upcoming events")
    else:
        print("Upcoming Event:",next_event['summary'])
        start_delta = (next_start - datetime.now()).total_seconds()
        print("Will start in", seconds_to_dhms(start_delta))

def seconds_to_dhms(seconds):
    days = seconds // (3600 * 24)
    hours = (seconds // 3600) % 24
    minutes = (seconds // 60) % 60
    return "{}{}{}{}{}{}{}{}".format(str(int(days)) + " day" if days > 0 else '','s' if days > 1 else '', ', ' if days > 0 else '',
                                    str(int(hours)) + " hour" if hours > 0 else '','s' if hours > 1 else '', ', ' if hours > 0 else '',
                                    str(int(minutes)) + " minute" if minutes > 0 else '','s' if minutes > 1 else '')

if __name__ == '__main__':
    main()