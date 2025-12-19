import os.path
import base64
from bs4 import BeautifulSoup
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from pathlib import Path
import csv

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def extract_body(payload):
    """Fonction récursive pour extraire et nettoyer le contenu du message"""
    data = None
    

    if 'body' in payload and 'data' in payload['body']:
        data = payload['body']['data']
    elif 'parts' in payload:
        for part in payload['parts']:

            if part['mimeType'] in ['text/plain', 'text/html']:
                data = part['body'].get('data')
                mime_type = part['mimeType']
                if data: break 
            elif 'parts' in part:
                return extract_body(part)

    if not data:
        return ""


    decoded_content = base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')


    soup = BeautifulSoup(decoded_content, 'html.parser')
    

    for script_or_style in soup(["script", "style"]):
        script_or_style.decompose()


    clean_text = soup.get_text(separator=' ')
    lines = (line.strip() for line in clean_text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    return '\n'.join(chunk for chunk in chunks if chunk)

def get_email_details(service, msg_id):
    """Récupère le sujet, l'expéditeur et le corps du message"""
    msg = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
    headers = msg['payload']['headers']
    
    details = {
        'id': msg_id,
        'subject': next((h['value'] for h in headers if h['name'] == 'Subject'), 'Sans objet'),
        'from': next((h['value'] for h in headers if h['name'] == 'From'), 'Inconnu'),
        'snippet': msg.get('snippet'), 
        'body': extract_body(msg['payload'])
    }
    return details


service = get_gmail_service()
results = service.users().messages().list(userId='me', maxResults=100).execute()
messages = results.get('messages', [])

# file = Path('list_mail')

# if not messages:
#     print("Aucun message trouvé.")
# else:
#     with file.open(mode='a', encoding='utf-8') as f:
#      for m in messages:
#         data = get_email_details(service, m['id'])
#         # ligne = f"ID: {data['id']} | De: {data['from']} | Sujet: {data['subject']}  | \n {data['body'][:100]}\n"
#         ligne = f"ID: {data['id']} | De: {data['from']} | Sujet: {data['subject']} | {data['body']} \n" # j'emleve les donnees pas utile pour mon modele
        
#         # On écrit dans le fichier
#         f.write(ligne)
#         print(f"Message {data['id']} enregistré.")



file_path = 'db.csv'
fieldnames = ['id', 'from', 'subject', 'body']


file_exists = os.path.exists(file_path)

with open(file_path, mode='a', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')

    if not file_exists or os.stat(file_path).st_size == 0:

        f.write("sep=;\n") 
        writer.writeheader()

    for m in messages:
        data = get_email_details(service, m['id'])
        
        row = {
            'id': data['id'],
            'from': data['from'],
            'subject': data['subject'],
            'body': data['body'][:100].replace('\n', ' ').replace('\r', '').replace(';', ',')
        }
        
        writer.writerow(row)
        print(f"Message {data['id']} enregistré.")