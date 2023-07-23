import json
import os
from os.path import join

import requests


class Http:
    @staticmethod
    def download_file(url, file_name, directory=os.getcwd()):
        data = {
            'request': 'download_http_file'
        }
        if url:
            status = 200
        else:
            status = 404
            data['response'] = 'URL not found'

        if status == 200:
            output_file_path = join(directory, file_name)
            try:
                file_download_response = requests.get(url)
                with open(output_file_path, 'wb') as f:
                    f.write(file_download_response.content)
                status = 200
                data['response'] = {'file': join(directory, file_name), 'downloaded': True}
            except Exception as e:
                status = 501
                data['response'] = {'file': join(directory, file_name), 'downloaded': False, 'error': str(e)}

        if status == 200:
            status_detail = 'success'
        else:
            status_detail = 'fail'
        return status, json.dumps({'status': status_detail, 'data': data})
