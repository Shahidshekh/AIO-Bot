import os
import pickle
import time
import googleapiclient.http
import asyncio

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from bot.modules.logger import LOGGER

creds = None
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'service_acc.json', ['https://www.googleapis.com/auth/drive'])
        creds = flow.run_local_server(port=0)
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)


async def upload_gd(file_path, message):
    file_name = os.path.basename(file_path)
    try:
        LOGGER.info("Generating service!!!!!!!!!!")
        LOGGER.info(f"creds - {creds}")
        gd_service = build("drive", "v3", credentials=creds)
        #0ALsEc-F8sH1NUk9PVA 
        asyncio.sleep(10)
        file_meta = {'name': file_name, 'parents': ["0ACb9rPBcPZC1Uk9PVA"]}
        media = googleapiclient.http.MediaFileUpload(file_path, resumable=True)
        
        file = gd_service.files().create(
            supportsTeamDrives=True,
            body=file_meta,
            media_body=media,
            fields="id"
        ).execute()

        response = None
        LOGGER.info("Going ON Loop!!!!!!!!!!!!")
        while response is None:
            status, response = file.next_chunk()
            if status:
                progress = int(status.progress(status.progess() * 100))
                message.edit(f'Progress : {progress}')
                time.sleep(3.0)

        await message.edit(f"Uploaded Successfully!\n\n**File Name** : {file_name}"
                           f"**Team Drive** : 0ACb9rPBcPZC1Uk9PVA")

    except HttpError as error:
        LOGGER.error("Error!!!!!!!!!!!")
        await message.edit(f"**Error** : {error}")

    except Exception as e:
        LOGGER.error("lol")
        await message.edit(f"**Error** : {e}")
