import os
import datetime
import pickle
import argparse
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dateutil import parser
import pytz

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def get_calendar_service():
    """Get an authorized Google Calendar API service instance."""
    creds = None
    # The file token.pickle stores the user's access and refresh tokens
    if os.path.exists('../token.pickle'):
        with open('../token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '../credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('../token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('calendar', 'v3', credentials=creds)


def get_availability(start_hour=9, end_hour=17, days=7, slot_duration=30, mode="both", debug=False):
    """Get availability from Google Calendar for the specified working hours and days."""
    service = get_calendar_service()

    # Get timezone from calendar
    calendar = service.calendars().get(calendarId='primary').execute()
    calendar_timezone = calendar.get('timeZone', 'UTC')
    local_tz = pytz.timezone(calendar_timezone)

    # Get current date in local timezone
    now = datetime.datetime.now(local_tz)
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)

    print(f"\nChecking availability for the next {days} days")
    print(f"Working hours: {start_hour}:00 to {end_hour}:00")
    print(f"Time zone: {calendar_timezone}")
    print("=" * 50)

    for day_offset in range(days):
        current_date = today + datetime.timedelta(days=day_offset)

        # Set working hours for the day
        day_start = current_date.replace(hour=start_hour, minute=0, second=0)
        day_end = current_date.replace(hour=end_hour, minute=0, second=0)

        # Format times for API in RFC3339 format
        time_min = day_start.isoformat()
        time_max = day_end.isoformat()

        # Get events for the day
        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])

        if debug:
            print(f"\nDEBUG: Found {len(events)} events for {current_date.strftime('%A, %B %d')}")
            for event in events:
                print(f"  Event: {event.get('summary', 'Untitled')}")
                print(f"  Status: {event.get('status', 'unknown')}")
                print(f"  Start: {event['start'].get('dateTime', event['start'].get('date', 'unknown'))}")
                print(f"  End: {event['end'].get('dateTime', event['end'].get('date', 'unknown'))}")
                print(f"  Creator: {event.get('creator', {}).get('email', 'unknown')}")
                print("  ---")

        # Create time slots for the day
        time_slots = []
        current_time = day_start
        while current_time < day_end:
            next_time = current_time + datetime.timedelta(minutes=slot_duration)
            time_slots.append((current_time, next_time))
            current_time = next_time

        # Mark slots that overlap with events as busy
        busy_slots = []
        free_slots = []

        for slot_start, slot_end in time_slots:
            is_free = True
            overlapping_event = None

            for event in events:
                # Only consider confirmed events (skip canceled or tentative)
                if event.get('status') != 'confirmed':
                    continue

                # Handle events where you're an attendee
                if 'attendees' in event:
                    self_attendee = next((a for a in event['attendees'] if a.get('self', False)), None)
                    if self_attendee and self_attendee.get('responseStatus') == 'declined':
                        continue  # Skip events you've declined

                # Get event start/end times
                event_start = event['start'].get('dateTime')
                event_end = event['end'].get('dateTime')

                # Handle all-day events
                if not event_start or not event_end:
                    event_date = event['start'].get('date')
                    if event_date:
                        event_date = datetime.datetime.strptime(event_date, '%Y-%m-%d').replace(tzinfo=local_tz)
                        # If it's an all-day event for this day, mark the whole day as busy
                        event_day = event_date.date()
                        slot_day = slot_start.date()
                        if event_day == slot_day:
                            is_free = False
                            overlapping_event = event
                            break
                    continue

                # Parse event times
                event_start_dt = parser.parse(event_start).astimezone(local_tz)
                event_end_dt = parser.parse(event_end).astimezone(local_tz)

                # Check for overlap - if the slot overlaps with the event at all, it's busy
                if max(slot_start, event_start_dt) < min(slot_end, event_end_dt):
                    is_free = False
                    overlapping_event = event
                    break

            if is_free:
                free_slots.append((slot_start, slot_end))
            else:
                event_summary = overlapping_event.get('summary', 'Busy') if overlapping_event else 'Busy'
                busy_slots.append((slot_start, slot_end, event_summary))

        # Print results for the day
        day_name = current_date.strftime("%A, %B %d")
        print(f"\nDay: {day_name}")

        # Print busy slots if requested
        if mode in ["busy", "both"]:
            print(f"  Busy times ({len(busy_slots)}):")
            if busy_slots:
                for start, end, summary in busy_slots:
                    print(f"    {start.strftime('%H:%M')} - {end.strftime('%H:%M')} : {summary}")
            else:
                print("    No busy slots")

        # Print free slots if requested
        if mode in ["free", "both"]:
            print(f"  Free times ({len(free_slots)}):")
            if free_slots:
                for start, end in free_slots:
                    print(f"    {start.strftime('%H:%M')} - {end.strftime('%H:%M')}")
            else:
                print("    No free slots")


def main():
    parser = argparse.ArgumentParser(description='Google Calendar Availability Checker')
    parser.add_argument('--days', type=int, default=5,
                        help='Number of days to check ahead (default: 5)')
    parser.add_argument('--start', type=int, default=9,
                        help='Start hour of working day, 24h format (default: 8)')
    parser.add_argument('--end', type=int, default=17,
                        help='End hour of working day, 24h format (default: 18)')
    parser.add_argument('--duration', type=int, default=30,
                        help='Duration of time slots in minutes (default: 30)')
    parser.add_argument('--mode', choices=['free', 'busy', 'both'], default='both',
                        help='What to display: free slots, busy slots, or both (default: both)')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug mode to see detailed event information')

    args = parser.parse_args()

    get_availability(
        start_hour=args.start,
        end_hour=args.end,
        days=args.days,
        slot_duration=args.duration,
        mode=args.mode,
        debug=args.debug
    )


if __name__ == '__main__':
    main()