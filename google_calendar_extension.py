import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
creds = Credentials.from_authorized_user_file("creds.json", SCOPES)
service = build("calendar", "v3", credentials=creds)

from jess_extension import jess_extension

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