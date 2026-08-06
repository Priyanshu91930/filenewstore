from google_auth_oauthlib.flow import InstalledAppFlow
flow = InstalledAppFlow.from_client_secrets_file(
    'client_secret.json',
    ['https://www.googleapis.com/auth/drive'],
    redirect_uri='http://localhost:8099'
)
creds = flow.run_local_server(port=8099, open_browser=True, success_message='✅ Authorization complete! You can close this window.')
with open('token.json', 'w') as f:
    f.write(creds.to_json())
print("✅ token.json generated")
