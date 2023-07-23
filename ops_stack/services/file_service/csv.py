import csv
import json
import os
from os.path import join, isfile


class CsvFile:
    @staticmethod
    def reader(file_name, directory=os.getcwd()):
        data = {
            'request': 'csv_reader'
        }
        csv_data = ""
        if isfile(join(directory, file_name)):
            try:
                data['response'] = []
                with open(join(directory, file_name)) as file:
                    csv_data = csv.reader(file)
                    data['response'] = 'csv file read success'
                status = 200
            except Exception as e:
                status = 406
                data['response'] = str(e)
        else:
            status = 404
            data['response'] = "File not found"

        if status == 200:
            status_detail = 'success'
        else:
            status_detail = 'fail'

        return status, json.dumps({'status': status_detail, 'data': data}), csv_data

    @staticmethod
    def writer(csv_data, file_name, directory=os.getcwd()):
        data = {
            'request': 'csv_writer'
        }
        try:
            with open(join(directory, file_name), mode='w', newline="") as file:
                csv_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                csv_writer.writerows(csv_data)
                status = 200
                data['response'] = {'file': join(directory, file_name), 'csv_created': True}
        except Exception as e:
            status = 502
            data['response'] = {'file': join(directory, file_name), 'csv_created': False, 'error': str(e)}

        if status == 200:
            status_detail = 'success'
        else:
            status_detail = 'fail'

        return status, json.dumps({'status': status_detail, 'data': data})

    @staticmethod
    def to_json(file_name, directory=os.getcwd()):
        data = {
            'request': 'csv-file_to_json'
        }
        if isfile(join(directory, file_name)):
            try:
                with open(join(directory, file_name), 'r') as file:
                    headers = next(file, None)
                    json_data = csv.DictReader(file, [x.strip() for x in headers.split(",")])
                    data['response'] = [row for row in json_data]
                    status = 200
            except Exception as e:
                status = 503
                data['response'] = str(e)
        else:
            status = 404
            data['response'] = "File not found"

        if status == 200:
            status_detail = 'success'
        else:
            status_detail = 'fail'

        return status, json.dumps({'status': status_detail, 'data': data})
