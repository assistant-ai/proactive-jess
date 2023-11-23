import datetime
import datetime
import dateparser

from typing import List

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]
try:
    creds = Credentials.from_authorized_user_file("creds.json", SCOPES)
    service = build("calendar", "v3", credentials=creds)
except Exception as e:
    pass

from extensions.jess_extension import jess_extension


@jess_extension(
    description="Create Google Calendar event, parameters will be passed as is to Google calendar API. When scheduling add user mail as well to the list of attendees",
    param_descriptions={
        "summary": "summary of the event",
        "location": "can be empty, location of the event",
        "description": "desription of the event",
        "start_timestamp": "date and time, free form, of the start of the event",
        "end_timestamp": "date and time, free form, of the end of the event",
        "attendee_mails": "list of mails of attendees, in a string, comma separated",
    }
)
def create_google_calendar_event(summary: str, location: str, description: str, start_timestamp: str, end_timestamp: str, attendee_mails: str):
    attendee_mails = attendee_mails.split(",")
    attendees = [{
        'email': mail
    } for mail in attendee_mails]
    start_date = dateparser.parse(start_timestamp)
    end_date = dateparser.parse(end_timestamp)
    event = {
        'summary': summary,
        'location': location,
        'description': description,
        'start': {
            'dateTime': start_date.isoformat(),
            'timeZone': 'America/Los_Angeles'
        },
        'end': {
            'dateTime': end_date.isoformat(),
            'timeZone': 'America/Los_Angeles'
        },
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
