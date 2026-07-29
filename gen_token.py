from google_auth_oauthlib.flow import InstalledAppFlow
flow = InstalledAppFlow.from_client_secrets_file(
    'client_secret.json',
    ['https://www.googleapis.com/auth/drive']
)
creds = flow.run_local_server(port=0, open_browser=True)
with open('token.json', 'w') as f:
    f.write(creds.to_json())
print("✅ token.json generated")
