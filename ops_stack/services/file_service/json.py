import json
import os
from os.path import join, isfile

import xmltodict
import yaml


class JsonFile:
    @staticmethod
    def reader(file_name, directory=os.getcwd()):
        data = {
            'request': 'json_reader'
        }
        json_data = ""
        if isfile(join(directory, file_name)):
            try:
                with open(join(directory, file_name)) as file:
                    data['response'] = 'json file read success'
                    json_data = json.load(file)
                status = 200
            except Exception as e:
                status = 501
                data['response'] = str(e)
        else:
            status = 404
            data['response'] = "File not found"

        if status == 200:
            status_detail = 'success'
        else:
            status_detail = 'fail'

        return status, json.dumps({'status': status_detail, 'data': data}), json_data

    @staticmethod
    def writer(json_data, file_name, directory=os.getcwd()):
        data = {
            'request': 'json_writer'
        }
        try:
            json_data = json.loads(json_data)
            with open(join(directory, file_name), 'w') as file:
                file.write(json.dumps(json_data, indent=4))
            status = 200
            data['response'] = {'file': join(directory, file_name), 'json_created': True}
        except Exception as e:
            status = 502
            data['response'] = {'file': join(directory, file_name), 'csv_created': False, 'error': str(e)}

        if status == 200:
            status_detail = 'success'
        else:
            status_detail = 'fail'

        return status, json.dumps({'status': status_detail, 'data': data})

    @staticmethod
    def to_csv(json_data, directory=os.getcwd(), data_source='file'):
        data = {
            'request': 'json-{}_to_csv'.format(data_source)
        }
        if data_source.lower() in ['file', 'data']:
            status = 200
            if data_source == 'file':
                if isfile(join(directory, json_data)):
                    try:
                        with open(join(directory, json_data)) as file:
                            json_data = json.load(file)
                    except Exception as e:
                        status = 503
                        data['response'] = str(e)
                else:
                    status = 404
                    data['response'] = "File not found"
            if data_source == 'data':
                try:
                    json_data = json.loads(json_data)
                except Exception as e:
                    status = 504
                    data['response'] = str(e)
            if status == 200:
                data['response'] = [list(json_data[0].keys())]
                for json_object in json_data:
                    data['response'].append(list(json_object.values()))
        else:
            status = 407
            data['response'] = "Unsupported data source {}".format(data_source)

        if status == 200:
            status_detail = 'success'
        else:
            status_detail = 'fail'

        return status, json.dumps({'status': status_detail, 'data': data})

    @staticmethod
    def to_xml_file(json_data, xml_file_name, data_source='file', directory=os.getcwd()):
        data = {
            'request': 'json-{}_to_xml'.format(data_source)
        }
        if data_source.lower() in ['file', 'data']:
            status = 200
            if data_source == 'file':
                if isfile(join(directory, json_data)):
                    try:
                        with open(join(directory, json_data)) as file:
                            json_data = json.load(file)
                    except Exception as e:
                        status = 503
                        data['response'] = str(e)
                else:
                    status = 404
                    data['response'] = "File not found"
            if data_source == 'data':
                try:
                    json_data = json.loads(json_data)
                except Exception as e:
                    status = 504
                    data['response'] = str(e)
            if status == 200:
                try:
                    xml_data = xmltodict.unparse(json_data, pretty=True)
                    with open(join(directory, xml_file_name), mode="w") as file:
                        file.write(xml_data)
                    data['response'] = {'file': join(directory, xml_file_name), 'xml_created': True}
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

    @staticmethod
    def to_yaml_file(json_data, yaml_file_name, directory=os.getcwd(), data_source='file'):
        data = {
            'request': 'yaml-{}_to_json'.format(data_source)
        }

        if data_source.lower() in ['file', 'data']:
            if data_source == 'file':
                if isfile(join(directory, json_data)):
                    try:
                        status, response = JsonFile.reader(file_name=json_data, directory=directory)
                        json_data = json.loads(response)['data']['response']
                    except Exception as e:
                        status = 504
                        data['response'] = str(e)
                else:
                    status = 404
                    data['response'] = "File not found"
            else:
                status = 404
                data['response'] = "File not found"
            if data_source == 'data':
                try:
                    json_data = json.loads(json_data)
                except Exception as e:
                    status = 505
                    data['response'] = str(e)
            if status == 200:
                try:
                    with open(join(directory, yaml_file_name), mode='w') as file:
                        yaml.dump(json_data, file, sort_keys=False)
                    data['response'] = {'file': join(directory, yaml_file_name), 'yaml_created': True}
                except Exception as e:
                    status = 506
                    data['response'] = str(e)
        else:
            status = 407
            data['response'] = "Unsupported data source {}".format(data_source)

        if status == 200:
            status_detail = 'success'
        else:
            status_detail = 'fail'
        return status, json.dumps({'status': status_detail, 'data': data})
