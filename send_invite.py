import os
import json
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

# Allow OAuth to work over HTTP in local development
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# FastAPI App
app = FastAPI()

# Google OAuth2 Settings
CLIENT_SECRETS_FILE = "credentials.json"  # Ensure this file exists in your project
SCOPES = ["https://www.googleapis.com/auth/calendar.events"]
REDIRECT_URI = "http://127.0.0.1:8000/auth/callback"

# Store user credentials
credentials = None

# OAuth Flow
flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES, redirect_uri=REDIRECT_URI)


@app.get("/auth")
async def auth():
    auth_url, state = flow.authorization_url(prompt="consent")
    return RedirectResponse(auth_url)


@app.get("/auth/callback")
async def auth_callback(request: Request):
    global credentials
    code = request.query_params.get("code")
    flow.fetch_token(code=code)
    credentials = flow.credentials
    return {"message": "Authentication successful! You can now create meetings."}


@app.post("/schedule_meeting")
async def schedule_meeting():
    global credentials
    if not credentials:
        return {"error": "User not authenticated. Please visit /auth first."}

    service = build("calendar", "v3", credentials=credentials)

    # Meeting details
    event = {
        "summary": "Team Meeting",
        "description": "Discussing project updates",
        "start": {"dateTime": "2025-02-04T10:00:00", "timeZone": "Asia/Kolkata"},
        "end": {"dateTime": "2025-02-04T11:00:00", "timeZone": "Asia/Kolkata"},
        "attendees": [{"email": "ramalakshmimoyilla@gmail.com"}],  # Change this to actual attendees
        "reminders": {"useDefault": True},
    }

    event_result = service.events().insert(calendarId="primary", body=event).execute()
    return {"message": "Meeting scheduled!", "event_link": event_result.get("htmlLink")}
