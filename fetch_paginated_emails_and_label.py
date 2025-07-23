import os
import csv
import re
import string
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# === Gmail API Setup ===
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def clean_text(text):
    text = text.lower()
    text = re.sub(r'\d+', '', text)
    text = text.translate(str.maketrans('', '', string.punctuation))
    return text.strip()

def fetch_paginated_emails(service, max_total=300, batch_size=100):
    all_messages = []
    next_page_token = None
    fetched = 0

    while fetched < max_total:
        response = service.users().messages().list(
            userId='me',
            labelIds=['INBOX'],
            maxResults=batch_size,
            pageToken=next_page_token
        ).execute()

        messages = response.get('messages', [])
        if not messages:
            break

        all_messages.extend(messages)
        fetched += len(messages)
        print(f"Fetched {fetched} emails...")

        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break  # No more pages

    return all_messages

def emails_label(service, messages, save_file='labeled_emails.csv'):

    # CSV Header
    with open(save_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['text', 'label'])

        for i, msg in enumerate(messages):
            msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
            snippet = msg_data.get('snippet', '')
            #snippet = clean_text(snippet)

            print("="*60)
            print(f"Email {i+1}:")
            print(snippet)
            print("="*60)
            label = input("Label this email as 'spam' or 'ham': ").strip().lower()
            while label not in ['spam', 'ham']:
                label = input("Invalid input. Please enter 'spam' or 'ham': ").strip().lower()

            writer.writerow([snippet, label])

    print(f"\n✅ Labeled dataset saved to {save_file}")

if __name__ == '__main__':
    service = get_gmail_service()

    messages = fetch_paginated_emails(service)

    emails_label(service,messages)