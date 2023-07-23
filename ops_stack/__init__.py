import fnmatch
import json
import os
import shutil
from os.path import join, isfile, isdir


class CommonMethods:
    @staticmethod
    def get_files_in_directory(directory=os.getcwd(), file_filter='*'):
        data = {
            'request': 'get_files_in_directory'
        }
        try:
            data['response'] = {'directory': directory, 'files': sorted(fnmatch.filter(os.listdir(directory), file_filter))}
            if data['response']['files']:
                status = 200
            else:
                status = 301
        except Exception as e:
            status = 500
            data['response'] = str(e)
        if status < 400:
            status_detail = 'success'
        else:
            status_detail = 'fail'

        return status, json.dumps({'status': status_detail, 'data': data})

    @staticmethod
    def clear_directory(directory=os.getcwd(), file_filter='*'):
        data = {
            'request': 'clear_directory'
        }
        response_status, response = CommonMethods.get_files_in_directory(directory, file_filter)
        if response_status == 200:
            status = 200
            data['response'] = {'directory': directory, 'files': []}
            for file in json.loads(response)['data']['response']['files']:
                file_object = {'file': file}
                try:
                    if isfile(join(directory, file)):
                        os.remove(join(directory, file))
                    elif isdir(join(directory, file)):
                        shutil.rmtree(join(directory, file))
                    file_object['removed'] = True
                except Exception as e:
                    file_object['removed'] = False
                    file_object['error'] = str(e)
                data['response']['files'].append(file_object)
        else:
            status = response_status
            data['response'] = json.loads(response)['data']['response']

        if status == 200:
            status_detail = 'success'
        else:
            status_detail = 'fail'

        return status, json.dumps({'status': status_detail, 'data': data})
