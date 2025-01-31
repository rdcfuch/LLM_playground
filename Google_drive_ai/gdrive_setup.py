import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from dotenv import load_dotenv

# Load existing .env file
load_dotenv()

# Google API configuration
SCOPES = ['https://www.googleapis.com/auth/drive']
CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
TOKEN_FILE = 'token.json'

def save_credentials_to_file(credentials):
    """Save the credentials to a file."""
    with open(TOKEN_FILE, 'w') as token_file:
        token_file.write(credentials.to_json())

def load_credentials_from_file():
    """Load the credentials from a file."""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as token_file:
            return Credentials.from_authorized_user_info(json.load(token_file))
    return None

def main():
    # Check if credentials are set in .env
    if not CLIENT_ID or not CLIENT_SECRET:
        print("Error: Missing Google credentials in .env file")
        print("1. Go to https://console.cloud.google.com/apis/credentials")
        print("2. Create OAuth 2.0 Client ID credentials (Web Application type)")
        print("3. Add http://localhost:8080 to authorized redirect URIs")
        print("4. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env")
        return

    # Try to load existing credentials from file
    credentials = load_credentials_from_file()

    # If no valid credentials, initiate the OAuth flow
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            # Refresh the token if expired
            credentials.refresh(Request())
        else:
            # Create flow instance
            flow = InstalledAppFlow.from_client_config(
                client_config={
                    "web": {
                        "client_id": CLIENT_ID,
                        "client_secret": CLIENT_SECRET,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": ["http://localhost:8080"]
                    }
                },
                scopes=SCOPES
            )

            # Run local server flow
            credentials = flow.run_local_server(
                port=8080,
                redirect_uri_trailing_slash=False,
                authorization_prompt_message="Please visit this URL: {url}",
                success_message="Authentication complete! You may close this window."
            )

        # Save the new credentials to a file
        save_credentials_to_file(credentials)

    print("Success! Authentication completed.")
    print(f"Access Token: {credentials.token}")
    print(f"Refresh Token: {credentials.refresh_token}")

if __name__ == '__main__':
    main()