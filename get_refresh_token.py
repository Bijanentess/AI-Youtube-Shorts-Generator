"""
Run this script ONCE locally on your machine to get your YOUTUBE_REFRESH_TOKEN.
Usage:
  python get_refresh_token.py
"""
import sys
from google_auth_oauthlib.flow import InstalledAppFlow

CLIENT_ID = input("Enter your YOUTUBE_CLIENT_ID: ").strip()
CLIENT_SECRET = input("Enter your YOUTUBE_CLIENT_SECRET: ").strip()

if not CLIENT_ID or not CLIENT_SECRET:
    print("Error: Client ID and Client Secret are required.")
    sys.exit(1)

flow = InstalledAppFlow.from_client_config(
    {
        "installed": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    },
    scopes=["https://www.googleapis.com/auth/youtube.upload"]
)

credentials = flow.run_local_server(port=8080)
print("\n" + "="*50)
print("SUCCESS! Your YOUTUBE_REFRESH_TOKEN is:")
print(credentials.refresh_token)
print("="*50)
print("Now add this as a secret named YOUTUBE_REFRESH_TOKEN in your GitHub repo!")
