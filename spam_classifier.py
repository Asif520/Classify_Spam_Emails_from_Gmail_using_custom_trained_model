import os
import base64
import joblib
import re
import string
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from bs4 import BeautifulSoup

# === SETUP ===
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


# === PREPROCESS FUNCTION (must match training) ===
def preprocess(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9!%@ ]+', '', text)
    text = text.translate(str.maketrans('', '', string.punctuation))

    text = text.strip()

    return text


# === LOAD TRAINED MODEL AND VECTORIZER ===
model = joblib.load('grid_svm_spam_classifier.pkl')
vectorizer = joblib.load("tf-idf_vectorizer.pkl")


def predict_spam(text):
    cleaned = preprocess(text)
    vect = vectorizer.transform([cleaned])
    result = model.predict(vect)[0]
    return "Spam" if result == 1 else "Ham"


# === GMAIL AUTHENTICATION ===
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


# === READ EMAILS AND PREDICT ===
def read_inbox():
    service = get_gmail_service()
    results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=50).execute()
    messages = results.get('messages', [])

    if not messages:
        print("No messages found.")
        return

    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        headers = msg_data['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "(No Subject)")
        snippet = msg_data.get('snippet', '')

        prediction = predict_spam(snippet)
        print("=" * 60)
        print(f"Subject: {subject}")
        print(f"Snippet: {snippet}")
        print(f"Prediction: {prediction}")


# === RUN ===
if __name__ == '__main__':
    read_inbox()
