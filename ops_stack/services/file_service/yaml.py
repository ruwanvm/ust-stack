import json
import os
from os.path import isfile, join

import yaml


class YamlFile:
    @staticmethod
    def reader(file_name, directory=os.getcwd()):
        data = {
            'request': 'yaml_reader'
        }

        yaml_data = ""

        if isfile(join(directory, file_name)):
            try:
                status = 200
                with open(join(directory, file_name)) as file:
                    yaml_data = yaml.load(file, Loader=yaml.FullLoader)
                data['response'] = 'yaml file read success'
            except Exception as e:
                status = 407
                data['response'] = str(e)
        else:
            status = 404
            data['response'] = "File not found"

        if status == 200:
            status_detail = 'success'
        else:
            status_detail = 'fail'
        return status, json.dumps({'status': status_detail, 'data': data}), yaml_data

    @staticmethod
    def writer(yaml_data, file_name, directory=os.getcwd()):
        data = {
            'request': 'yaml_writer'
        }

        try:
            status = 200
            with open(join(directory, file_name), mode='w') as file:
                yaml.dump(yaml_data, file, sort_keys=False)
                data['response'] = {'file': join(directory, file_name), 'yaml_created': True}
        except Exception as e:
            status = 408
            data['response'] = str(e)

        if status == 200:
            status_detail = 'success'
        else:
            status_detail = 'fail'
        return status, json.dumps({'status': status_detail, 'data': data})

    @staticmethod
    def to_json(yaml_data, directory=os.getcwd(), data_source='file'):
        data = {
            'request': 'yaml-{}_to_json'.format(data_source)
        }

        if data_source.lower() in ['file', 'data']:
            status = 200
            if data_source == 'file':
                if isfile(join(directory, yaml_data)):
                    status, response = YamlFile.reader(file_name=yaml_data, directory=directory)
                    data['response'] = json.loads(response)['data']['response']
                else:
                    status = 404
                    data['response'] = "File not found"
            if data_source == 'data':
                try:
                    data['response'] = yaml_data
                except Exception as e:
                    status = 504
                    data['response'] = str(e)
        else:
            status = 407
            data['response'] = "Unsupported data source {}".format(data_source)

        if status == 200:
            status_detail = 'success'
        else:
            status_detail = 'fail'
        return status, json.dumps({'status': status_detail, 'data': data})
