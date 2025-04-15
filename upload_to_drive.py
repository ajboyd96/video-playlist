# playlist_email.py
import os
import sys
import time
import pickle
import json
import mimetypes
import smtplib
from email.message import EmailMessage
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from jinja2 import Environment, FileSystemLoader

SCOPES = ['https://www.googleapis.com/auth/drive']
BASE_PATH = '/Volumes/easystore/courses'
UPLOADS_FOLDER_NAME = "Python Uploads"

EMAIL_SENDER = "ajboyd96@gmail.com"
EMAIL_PASSWORD = "jetdwfqlfdealacs"
EMAIL_RECIPIENT = "ajboyd96@gmail.com"
EMAIL_SUBJECT = "Your Playlist Link"

PLAYLIST_JSON_NAME = "playlist.json"
PLAYLIST_HTML_NAME = "playlist.html"
VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.flv'}
TOKEN_PICKLE = 'token.pickle'
CREDENTIALS_FILE = 'credentials.json'


def authenticate():
    creds = None
    if os.path.exists(TOKEN_PICKLE):
        with open(TOKEN_PICKLE, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PICKLE, 'wb') as token:
            pickle.dump(creds, token)
    return build('drive', 'v3', credentials=creds)


def get_drive_folder(service, name, parent_id=None):
    query = f"name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    else:
        query += " and 'root' in parents"
    results = service.files().list(q=query, fields="files(id)").execute()
    items = results.get('files', [])
    return items[0]['id'] if items else None


def get_or_create_drive_folder(service, name, parent_id=None, folder_cache={}):
    key = (name, parent_id)
    if key in folder_cache:
        return folder_cache[key]
    folder_id = get_drive_folder(service, name, parent_id)
    if not folder_id:
        metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id] if parent_id else []
        }
        folder = service.files().create(body=metadata, fields='id').execute()
        folder_id = folder.get('id')
    folder_cache[key] = folder_id
    return folder_id


def list_drive_files_recursive(service, folder_id):
    results = []
    page_token = None
    query = f"'{folder_id}' in parents and trashed=false"
    while True:
        response = service.files().list(q=query, fields="nextPageToken, files(id, name, mimeType)", pageToken=page_token).execute()
        for item in response.get('files', []):
            if item['mimeType'] == 'application/vnd.google-apps.folder':
                results.extend(list_drive_files_recursive(service, item['id']))
            else:
                results.append(item)
        page_token = response.get('nextPageToken')
        if not page_token:
            break
    return results


def set_file_public(service, file_id):
    try:
        service.permissions().create(
            fileId=file_id,
            body={'role': 'reader', 'type': 'anyone'},
            fields='id'
        ).execute()
    except Exception as e:
        print(f"Error setting file public: {e}")


def get_file_link(file_id):
    return f"https://drive.google.com/uc?export=view&id={file_id}"


def generate_playlist_files(video_entries, output_dir):
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('playlist_template.html')
    rendered_html = template.render(video_entries=video_entries)

    playlist_json = json.dumps(video_entries, indent=2)
    playlist_json_path = os.path.join(output_dir, PLAYLIST_JSON_NAME)
    playlist_html_path = os.path.join(output_dir, PLAYLIST_HTML_NAME)

    with open(playlist_json_path, "w", encoding="utf-8") as f:
        f.write(playlist_json)
    with open(playlist_html_path, "w", encoding="utf-8") as f:
        f.write(rendered_html)

    return playlist_json_path, playlist_html_path


def send_email(playlist_link):
    msg = EmailMessage()
    msg['Subject'] = EMAIL_SUBJECT
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECIPIENT
    msg.set_content(f"Here is your playlist link:\n\n{playlist_link}")

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")


def upload_file(service, filepath, filename, parent_id, mime_type):
    metadata = {'name': filename, 'parents': [parent_id]}
    media = MediaFileUpload(filepath, mimetype=mime_type, resumable=True)
    file = service.files().create(body=metadata, media_body=media, fields='id').execute()
    return file.get('id')


def main():
    service = authenticate()
    folders = [f for f in os.listdir(BASE_PATH) if os.path.isdir(os.path.join(BASE_PATH, f))]

    if len(sys.argv) < 2:
        print("Usage: python playlist_email.py <folder_number>")
        for idx, name in enumerate(folders, 1):
            print(f"{idx}. {name}")
        return

    try:
        folder_idx = int(sys.argv[1])
        folder_name = folders[folder_idx - 1]
    except:
        print("Invalid folder number.")
        return

    uploads_root_id = get_or_create_drive_folder(service, UPLOADS_FOLDER_NAME)
    drive_folder_id = get_drive_folder(service, folder_name, uploads_root_id)
    if not drive_folder_id:
        print(f"Drive folder '{folder_name}' not found under '{UPLOADS_FOLDER_NAME}'. Upload it first.")
        return

    files = list_drive_files_recursive(service, drive_folder_id)
    video_entries = []
    for file in files:
        name = file['name']
        ext = os.path.splitext(name)[1].lower()
        if ext in VIDEO_EXTENSIONS:
            set_file_public(service, file['id'])
            link = get_file_link(file['id'])
            video_entries.append({"title": name, "url": link})

    if not video_entries:
        print("No video files found.")
        return

    output_dir = os.path.join(os.getcwd(), "temp_playlist")
    os.makedirs(output_dir, exist_ok=True)
    playlist_json, playlist_html = generate_playlist_files(video_entries, output_dir)

    uploaded_link = None
    for file_path in [playlist_json, playlist_html]:
        filename = os.path.basename(file_path)
        mime, _ = mimetypes.guess_type(filename)
        file_id = upload_file(service, file_path, filename, drive_folder_id, mime)
        if filename.endswith(".html"):
            set_file_public(service, file_id)
            uploaded_link = get_file_link(file_id)
            print("Playlist HTML link:", uploaded_link)

    if uploaded_link:
        send_email(uploaded_link)

if __name__ == '__main__':
    main()
