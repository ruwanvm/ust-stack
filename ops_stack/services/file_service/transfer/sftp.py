import json
import os
import time
from os.path import join
import pysftp


class Sftp:
    def __init__(self, host, username, password):
        self.sftp_connected = False
        try:
            self.sftp_connected = True
            cnopts = pysftp.CnOpts()
            cnopts.hostkeys = None
            self.sftp_connection = pysftp.Connection(host, username=username,
                                                     password=password, cnopts=cnopts)
            print("Connected to {}".format(host))
            self.sftp__details = "SFTP connection success"
        except Exception as e:
            self.sftp__details = "SFTP connection fail : {}".format(str(e))

    def get_files_list(self, sftp_directory="/"):
        data = {
            'request': 'get_sftp_files_list'
        }
        if self.sftp_connected:
            try:
                with self.sftp_connection.cd(sftp_directory):
                    files_list = self.sftp_connection.listdir()
                status = 200
                data['response'] = {'sftp directory': sftp_directory, 'files': files_list}
            except Exception as e:
                status = 501
                data['response'] = str(e)
        else:
            status = 501
            data['response'] = self.sftp__details

        if status == 200:
            status_detail = 'success'
        else:
            status_detail = 'fail'
        return status, json.dumps({'status': status_detail, 'data': data})

    def download_file(self, file_name, sftp_directory="/", local_directory=os.getcwd(), local_file_name='default'):
        data = {
            'request': 'download_sftp_file'
        }
        if self.sftp_connected:
            try:
                if local_file_name.lower() == 'default':
                    local_file_name = file_name
                with self.sftp_connection.cd(sftp_directory):
                    self.sftp_connection.get(file_name, join(local_directory, local_file_name))
                status = 200
                data['response'] = {'file': join(local_directory, local_file_name), 'downloaded': True}
            except Exception as e:
                status = 502
                data['response'] = {'file': join(local_directory, local_file_name), 'downloaded': False,
                                    'error': str(e)}
        else:
            status = 501
            data['response'] = self.sftp__details

        if status == 200:
            status_detail = 'success'
        else:
            status_detail = 'fail'
        return status, json.dumps({'status': status_detail, 'data': data})

    def upload_file(self, file_name, local_directory=os.getcwd(), sftp_directory="/", sftp_file_name='default'):
        data = {
            'request': 'upload_sftp_file'
        }
        if self.sftp_connected:
            try:
                if sftp_file_name.lower() == 'default':
                    sftp_file_name = file_name
                file_path = join(local_directory, file_name)
                with self.sftp_connection.cd(sftp_directory):
                    self.sftp_connection.put(file_path, file_name)
                status = 200
                data['response'] = {'file': '{}/{}'.format(sftp_directory, sftp_file_name), 'uploaded': True}
            except Exception as e:
                status = 503
                data['response'] = {'file': '{}/{}'.format(sftp_directory, sftp_file_name), 'uploaded': False,
                                    'error': str(e)}
        else:
            status = 501
            data['response'] = self.sftp__details

        if status == 200:
            status_detail = 'success'
        else:
            status_detail = 'fail'
        return status, json.dumps({'status': status_detail, 'data': data})

    def wait_file(self, file_name, sftp_directory="/"):
        sftp_file_path = "{}/{}".format(sftp_directory, file_name)
        second = 0
        with self.sftp_connection.cd(sftp_directory):
            while not self.sftp_connection.exists(sftp_file_path):
                m, s = divmod(second, 60)
                h, m = divmod(m, 60)
                print("Time Elapsed: {:d}:{:02d}:{:02d}".format(h, m, s), end="\r")
                time.sleep(1)
                second = second + 1

    def read_file(self, file_name, sftp_directory="/"):
        data = {
            'request': 'read_sftp_file'
        }
        try:
            with self.sftp_connection.cd(sftp_directory):
                sftp_file = self.sftp_connection.open(file_name, mode='r')
                sftp_file_content = []
                for line in sftp_file.readlines():
                    sftp_file_content.append(line.rstrip())
            status = 200
            data['response'] = {'file': '{}/{}'.format(sftp_directory, file_name), 'read': True,
                                'content': '\n'.join(sftp_file_content)}
        except Exception as e:
            status = 504
            data['response'] = {'file': '{}/{}'.format(sftp_directory, file_name), 'read': False, 'error': str(e)}

        if status == 200:
            status_detail = 'success'
        else:
            status_detail = 'fail'
        return status, json.dumps({'status': status_detail, 'data': data})

    def close_connection(self):
        if self.sftp_connected:
            try:
                self.sftp_connection.close()
                print("SFTP connection disconnected")
            except Exception as e:
                raise ValueError(str(e))
        else:
            print("Not connected to SFTP")
