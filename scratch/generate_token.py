import os
import sys
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

# Scopes required to upload and set permissions on Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive']

def main():
    credentials_file = 'credentials.json'
    
    if not os.path.exists(credentials_file):
        print("\n❌ Error: 'credentials.json' not found in the root directory!")
        print("Please follow these steps to download it:")
        print("1. Go to Google Cloud Console: https://console.cloud.google.com/")
        print("2. Select your project: 'viralverse2026' (or whichever project you enabled Drive API on)")
        print("3. Go to 'APIs & Services' > 'Credentials'")
        print("4. Click '+ CREATE CREDENTIALS' and select 'OAuth client ID'")
        print("5. (If prompted) Configure your OAuth Consent Screen as 'External' and add 'Google Drive API' scopes, and add your email to Test Users.")
        print("6. Select Application Type: 'Desktop app' and click Create.")
        print("7. Download the client secret JSON file, rename it to 'credentials.json', and place it in the root folder of this bot.")
        return
        
    print("🔄 Initializing OAuth2 Flow...")
    try:
        flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
        creds = flow.run_local_server(port=0)
        
        # Save credentials to token.json
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            
        print("\n✅ Success! 'token.json' has been generated successfully.")
        print("Please copy 'token.json' to the root directory of your bot on your PC and VPS.")
    except Exception as e:
        print(f"\n❌ Error during OAuth Flow: {e}")

if __name__ == '__main__':
    main()
