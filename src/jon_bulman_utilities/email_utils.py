# For sending emails using Gmail API
import os

import google.auth.transport.requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
    

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]

def send_email(credentials, token_file, to, subject, body,
             cc=None, bcc=None, attachment=None):

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        print("No credentials or valid token")
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing auth token")
            request = google.auth.transport.requests.Request()
            try:
                creds.refresh(request)
            except OSError as e:
                print(f"How exceptional! {e}")
                result = f"A refresh error occurred - new token needed - delete {token_file}"
                print(result)
                return result
        else:
            print("Creating credentials token", credentials)
            flow = InstalledAppFlow.from_client_secrets_file( credentials, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_file, "w") as token:
            print("Writing token",token_file)
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds, cache_discovery=False)
        message = MIMEMultipart()

        # HTML body
        message.attach(MIMEText(body, 'html'))

        if attachment and os.path.exists(attachment):

            with open(attachment, "rb") as fh:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(fh.read())

            encoders.encode_base64(part)

            part.add_header(
                "Content-Disposition",
                f'attachment; filename="{os.path.basename(attachment)}"'
            )

            message.attach(part)

        if to is not None and len(to) > 0:        
            message['to'] = to
        if cc is not None and len(cc) > 0:
            message['cc'] = cc
        if bcc is not None and len(bcc) > 0:
            message['bcc'] = bcc
        message['subject'] = subject
        
        raw = base64.urlsafe_b64encode(
            message.as_bytes()
        ).decode()

        create_message = {'raw': raw}

        service.users().messages().send(
            userId="me",
            body=create_message
        ).execute()

        result = f"Message sent to {to}, Subject: {subject}"
        #print(f"Message sent to {results} Message Id: {results['id']}")

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        result = f"An error occurred: {error}"
        print(result)

    return result
