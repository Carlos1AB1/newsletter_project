from google_auth_oauthlib.flow import InstalledAppFlow
import pickle
import os

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def main():
    flow = InstalledAppFlow.from_client_secrets_file(
        r'C:\Users\ByArc\Downloads\client_secret_293312577050-lpq0j0vajgip7jt29su0mu03q0i63j2e.apps.googleusercontent.com.json', SCOPES)
    creds = flow.run_local_server(port=0)
    with open('token.json', 'wb') as token:
        pickle.dump(creds, token)

if __name__ == '__main__':
    main()
