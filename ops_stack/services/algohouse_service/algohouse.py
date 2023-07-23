import json
from datetime import datetime
from ops_stack.services.date_service import DateTime

import requests


class Algohouse:
    def __init__(self, url, username, key_id, secret_key):
        self.url = url
        login_url = "{}LoginService/APIKeyLoginCheck".format(self.url)
        payload = {'username': username, 'keyId': key_id, 'secretKey': secret_key}
        headers = {'Content-Type': 'application/json'}

        response = requests.request('POST', login_url, headers=headers, data=json.dumps(payload),
                                    allow_redirects=False, timeout=10)
        response_json = json.loads(response.text)
        if response_json['status'] == 'SUCCESS':
            self.status = 200
            algohouse_username = json.loads(response_json['reason'])['username']
            self.token = json.loads(response_json['reason'])['token']
            self.status_details = "Authenticated to Algohouse as {}".format(algohouse_username)
        else:
            self.status = 404
            self.status_details = "Algohouse connection is not authorized"

    def download_algohouse_reports(self, report_type, report_request_date="today", regenerate=False):
        data = {
            'request': f'download_{report_type}'
        }
        if self.status == 200:
            try:
                status = 200
                user_service_url = "{}UserService/{}".format(self.url, report_type)
                if report_request_date == "today":
                    user_service_rq_date = datetime.strptime(DateTime.today(), "%Y/%m/%d %H:%M:%S.%f")
                else:
                    user_service_rq_date = datetime.strptime(report_request_date, "%Y/%m/%d")
                payload = {'userId': '000001', 'date': user_service_rq_date.strftime("%Y-%m-%d"),
                           'regenerate': regenerate}
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer {}'.format(self.token)
                }
                response = json.loads(requests.request('POST', user_service_url, headers=headers,
                                                            data=json.dumps(payload), allow_redirects=False,
                                                            timeout=10).text)
                data['response'] = {'file_url': response['fileUrl']}
            except Exception as e:
                status = 501
                data['response'] = str(e)
        else:
            status = self.status
            data['response'] = self.status_details

        if status == 200:
            status_detail = 'success'
        else:
            status_detail = 'fail'

        return status, json.dumps({'status': status_detail, 'data': data})
