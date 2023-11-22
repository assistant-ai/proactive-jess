import datetime
import os.path
import json
import datetime
import pytz

from typing import List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]
creds = Credentials.from_authorized_user_file("creds.json", SCOPES)
service = build("calendar", "v3", credentials=creds)

from jess_extension import jess_extension


def _convert_timestamp_to_datetime(timestamp, timezone_str='America/Los_Angeles'):
    # Convert the integer timestamp to a datetime object
    dt = datetime.datetime.fromtimestamp(timestamp, tz=pytz.utc)

    # Convert the datetime object to the desired timezone
    desired_timezone = pytz.timezone(timezone_str)
    localized_dt = dt.astimezone(desired_timezone)

    # Format the datetime object as a string
    formatted_datetime = localized_dt.strftime('%Y-%m-%dT%H:%M:%S%z')

    return {
        'dateTime': formatted_datetime,
        'timeZone': timezone_str
    }


@jess_extension(
    description="Create Google Calendar event, parameters will be passed as is to Google calendar API. When scheduling add user mail as well to the list of attendees",
    param_descriptions={
        "summary": "summary of the event",
        "location": "can be empty, location of the event",
        "description": "desription of the event",
        "start_timestamp": "timestamp, int, of the start of the event",
        "end_timestamp": "timestamp, int, of the end of the event",
        "attendee_mails": "list of mails of attendees",
    }
)
def create_google_calendar_event(summary: str, location: str, description: str, start_timestamp: int, end_timestamp: int, attendee_mails: List[str]):
    attendees = [{
        'email': mail
    } for mail in attendee_mails]
    event = {
        'summary': summary,
        'location': location,
        'description': description,
        'start': _convert_timestamp_to_datetime(start_timestamp),
        'end': _convert_timestamp_to_datetime(end_timestamp),
        'attendees': attendees
    }
    event = service.events().insert(calendarId='primary', body=event).execute()
    return f"Event created: {event.get('htmlLink')}"


@jess_extension(
    description="Get upcoming events from user's Google Calenda",
    param_descriptions={
        "count": "Numbe of upcoming events to get"
    }
)
def get_upcoming_calendar_events(count: int):
    try:
        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + "Z"  
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=count,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            return "No upcoming events found."
        else:
            result = ""
            # Prints the start and name of the next 10 events
            for event in events:
                start = event["start"].get("dateTime", event["start"].get("date"))
                result = result + start + ": " + event["summary"] + "\n"
            return result

    except HttpError as error:
        return f"An error occurred: {error}"
