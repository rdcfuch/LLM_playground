import os
from google_auth_oauthlib.flow import InstalledAppFlow
from dotenv import load_dotenv

# Load existing .env file
load_dotenv()

# Google API configuration
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

def main():
    if not CLIENT_ID or not CLIENT_SECRET:
        print("Error: Missing Google credentials in .env file")
        print("1. Go to https://console.cloud.google.com/apis/credentials")
        print("2. Create OAuth 2.0 Client ID credentials (Web Application type)")
        print("3. Add http://localhost:8080 to authorized redirect URIs")
        print("4. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env")
        return

    # Create flow instance
    flow = InstalledAppFlow.from_client_config(
        client_config={
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://accounts.google.com/o/oauth2/token"
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
    
    # Write refresh token to .env
    with open('.env', 'a') as f:
        print(credentials.refresh_token)
        f.write(f'\nGOOGLE_REFRESH_TOKEN={credentials.refresh_token}')
    
    print("Success! Refresh token added to .env file")

if __name__ == '__main__':
    main()