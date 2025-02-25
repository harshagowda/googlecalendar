# googlecalendar
# Google Calendar Availability Checker

A command-line tool that helps you check free and busy times in your Google Calendar.

## Features

- View your busy/occupied time slots
- Find available time slots in your calendar
- Customizable working hours and time slot duration
- Support for multiple days of availability checking
- Command-line arguments for easy integration with scripts

## Prerequisites

- Python 3.6 or higher
- A Google account with Calendar enabled
- Google Cloud project with the Google Calendar API enabled

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/calendar-availability-checker.git
   cd calendar-availability-checker
   ```

2. Install the required dependencies:
   ```bash
   pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib python-dateutil pytz
   ```

## Google API Setup (Detailed Steps)

Before using the script, you need to set up the Google Calendar API:

1. **Create a Google Cloud Project**:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Click on "Select a project" at the top of the page, then click "New Project"
   - Enter a name for your project and click "Create"

2. **Enable the Google Calendar API**:
   - In your project, go to "APIs & Services" > "Library"
   - Search for "Google Calendar API"
   - Click on the "Google Calendar API" result and click "Enable"

3. **Create OAuth 2.0 Credentials**:
   - Go to "APIs & Services" > "Credentials" 
   - Click "Create Credentials" and select "OAuth client ID"
   - If prompted to configure the consent screen, click "Configure Consent Screen"
     - Choose "External" as the user type (or "Internal" if using Google Workspace)
     - Fill in the required fields (App name, User support email, Developer contact information)
     - Click "Save and Continue" through the next screens (you can leave most fields blank)
     - Click "Back to Dashboard" when done
   - Now create credentials:
     - Go back to "Credentials" and click "Create Credentials" > "OAuth client ID"
     - Select "Desktop app" as the application type
     - Give your OAuth client a name (e.g., "Calendar Availability Checker")
     - Click "Create"
   - Download the credentials by clicking the download icon (JSON file)
   - Save the downloaded file as `credentials.json` in the same directory as the script

4. **Add Yourself as a Test User** (if using external user type):
   - Go to "APIs & Services" > "OAuth consent screen"
   - Scroll down to "Test users" section
   - Click "+ ADD USERS"
   - Add your Google email address
   - Click "SAVE"

## Usage

Run the script using Python:

```bash
python google_calendar_get_free_slots.py
```

### Command-Line Arguments

Customize the script behavior with these arguments:

- `--days NUMBER`: Number of days to check ahead (default: 5)
- `--start HOUR`: Start hour of working day, 24h format (default: 9)
- `--end HOUR`: End hour of working day, 24h format (default: 17)
- `--duration MINUTES`: Duration of time slots in minutes (default: 30)
- `--mode MODE`: What to display: free, busy, or both (default: both)
- `--debug`: Enable debug mode to show detailed event information

### Examples

Check availability for the next 7 days:
```bash
python google_calendar_get_free_slots.py --days 7
```

Check evening availability from 6 PM to 10 PM:
```bash
python google_calendar_get_free_slots.py --start 18 --end 22
```

Show only free time slots in 1-hour increments:
```bash
python google_calendar_get_free_slots.py --mode free --duration 60
```

### First Run Authentication

The first time you run the script:
1. A browser window will open and prompt you to log in with your Google account
2. Grant the requested permissions to access your calendar
3. The authentication token will be saved locally for future use

## Output Format

The script provides a clear, readable output of your calendar availability:

```
Checking availability for the next 5 days
Working hours: 9:00 to 17:00
Time zone: America/Denver
==================================================

Day: Monday, February 24
  Busy times (1):
    11:00 - 11:30 : Harsha Gowda + XXXXXX
  Free times (15):
    09:00 - 09:30
    09:30 - 10:00
    ...

Day: Tuesday, February 25
  Busy times (3):
    09:30 - 10:00 : Recruiter 30 min Call with XXXXX XXXX
    12:30 - 13:00 : Interview with XXXXX XXXXX
    13:30 - 14:00 : Recruiter Screen Harsha Krishne Gowda XXXXXX
  Free times (13):
    09:00 - 09:30
    10:00 - 10:30
    ...
```

## Security Notes

- The script uses OAuth 2.0 for secure authentication
- All access tokens are stored locally on your machine
- The script only requests read-only access to your calendar
- No calendar data is sent to any third-party servers

## Troubleshooting

If you encounter issues:

1. **API Quota Errors**: The Google Calendar API has usage limits. For personal use, you're unlikely to hit these limits.

2. **Authentication Errors**: Make sure your `credentials.json` file is correctly placed in the script directory. If issues persist, delete the `token.pickle` file and run the script again to re-authenticate.

3. **Calendar Event Detection Issues**: Use the `--debug` flag to see detailed information about the events being found in your calendar.

4. **Timezone Issues**: The script uses your Google Calendar's timezone settings. Make sure your calendar timezone is correctly set.

## License

[MIT License](LICENSE)

## Acknowledgments

- Google Calendar API
- Google API Python Client
