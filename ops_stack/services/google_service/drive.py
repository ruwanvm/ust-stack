import json
import os
from os.path import join

from googleapiclient.discovery import build
from httplib2 import Http
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from oauth2client.service_account import ServiceAccountCredentials


class Gdrive:
    def __init__(self, gdrive_credentials_file, gdrive_scopes='https://www.googleapis.com/auth/drive'):
        self.connected = False
        try:
            self.connected = True
            creds = ServiceAccountCredentials.from_json_keyfile_name(gdrive_credentials_file, gdrive_scopes)
            self.google_drive_service = build('drive', 'v3', http=creds.authorize(Http()))
            self.connection_details = "Google drive connection success"
        except Exception as e:
            self.connection_details = "Google drive connection fail : {}".format(str(e))

    def upload_csv_file(self, drive_directory_id, file_name, local_directory=os.getcwd(), drive_file_name='default'):
        data = {
            'request': 'upload_file_google-drive'
        }
        if self.connected:
            try:
                status = 200
                if drive_file_name == 'default':
                    drive_file_name = file_name
                file_metadata = {'name': drive_file_name, 'parents': [drive_directory_id]}
                media = MediaFileUpload(join(local_directory, file_name), mimetype='text/csv', resumable=True)
                file = self.google_drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
                data['response'] = {'file': file.get('id'), 'uploaded': True}
            except Exception as e:
                status = 503
                data['response'] = {'file': file_name, 'uploaded': False, 'error': str(e)}
        else:
            status = 500
            data['response'] = self.connection_details

        if status == 200:
            status_detail = 'success'
        else:
            status_detail = 'fail'
        return status, json.dumps({'status': status_detail, 'data': data})
