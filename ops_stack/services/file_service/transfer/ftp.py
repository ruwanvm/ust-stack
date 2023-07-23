import json
import os
from ftplib import FTP_TLS, FTP
from os.path import join


class Ftp:
    def __init__(self, host, username, password, secure=False):
        self.ftp_connected = False
        try:
            self.ftp_connected = True
            if secure:
                self.ftp_connection = FTP_TLS(host)
                self.ftp_connection.login(username, password)
                self.ftp_connection.prot_p()
                self.ftp__details = "FTPS connection success"
            else:
                self.ftp_connection = FTP(host)
                self.ftp_connection.login(username, password)
                self.ftp__details = "FTP connection success"
            print("Connected to {}".format(host))
        except Exception as e:
            self.ftp_details = "FTP connection fail : {}".format(str(e))

    def get_files_list(self, ftp_directory="/"):
        data = {
            'request': 'get_ftp_files_list'
        }
        if self.ftp_connected:
            try:
                self.ftp_connection.cwd(ftp_directory)
                files_list = self.ftp_connection.nlst()
                status = 200
                data['response'] = {'ftp directory': ftp_directory, 'files': files_list}
            except Exception as e:
                status = 501
                data['response'] = str(e)
        else:
            status = 500
            data['response'] = self.ftp_details

        if status == 200:
            status_detail = 'success'
        else:
            status_detail = 'fail'
        return status, json.dumps({'status': status_detail, 'data': data})

    def download_file(self, file_name, ftp_directory="/", local_directory=os.getcwd(), local_file_name='default'):
        data = {
            'request': 'download_ftp_file'
        }
        if self.ftp_connected:
            try:
                if local_file_name.lower() == 'default':
                    local_file_name = file_name
                output_file_path = join(local_directory, local_file_name)
                output_file = open(output_file_path, 'wb')
                self.ftp_connection.cwd(ftp_directory)
                self.ftp_connection.retrbinary('RETR {}'.format(file_name), output_file.write)
                status = 200
                data['response'] = {'file': join(local_directory, local_file_name), 'downloaded': True}
                output_file.close()
            except Exception as e:
                status = 502
                data['response'] = {'file': join(local_directory, local_file_name), 'downloaded': False, 'error': str(e)}
        else:
            status = 500
            data['response'] = self.ftp_details

        if status == 200:
            status_detail = 'success'
        else:
            status_detail = 'fail'
        return status, json.dumps({'status': status_detail, 'data': data})

    def upload_file(self, file_name, local_directory=os.getcwd(), ftp_directory="/", ftp_file_name='default'):
        data = {
            'request': 'upload_ftp_file'
        }
        if self.ftp_connected:
            try:
                if ftp_file_name.lower() == 'default':
                    ftp_file_name = file_name
                local_file_path = join(local_directory, file_name)
                file_to_upload = open(local_file_path, 'rb')
                ftp_file_path = join(ftp_directory, file_name)
                self.ftp_connection.cwd(ftp_directory)
                self.ftp_connection.storbinary('STOR {}'.format(ftp_file_path), file_to_upload)
                status = 200
                data['response'] = {'file': '{}/{}'.format(ftp_directory, ftp_file_name), 'uploaded': True}
            except Exception as e:
                status = 503
                data['response'] = {'file': '{}/{}'.format(ftp_directory, ftp_file_name), 'uploaded': False, 'error': str(e)}
        else:
            status = 500
            data['response'] = self.ftp_details

        if status == 200:
            status_detail = 'success'
        else:
            status_detail = 'fail'
        return status, json.dumps({'status': status_detail, 'data': data})

    def close_connection(self):
        if self.ftp_connected:
            try:
                self.ftp_connection.quit()
                print("ftp connection disconnected")
            except Exception as e:
                raise ValueError(str(e))
        else:
            print("Not connected to FTP")
