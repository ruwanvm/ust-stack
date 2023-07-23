from datetime import datetime, timedelta
import json
import requests
from pytz import timezone


class TradingDays:
    def __init__(self, tradier_api_key):
        self.tradier_api_key = tradier_api_key
        self.time_zone = timezone('US/Eastern')

    def trading_dates_of_month(self, year="This_Year", month="This_Month"):
        data = {
            'request': 'trading_dates_of_month'
        }
        if year == "This_Year":
            year = datetime.now(self.time_zone).strftime("%Y")
        if month == "This_Month":
            month = datetime.now(self.time_zone).strftime("%m")
        try:
            status = 200
            response = requests.get('https://api.tradier.com/v1/markets/calendar',
                                    params={'month': month, 'year': year},
                                    headers={'Authorization': 'Bearer {}'.format(self.tradier_api_key),
                                             'Accept': 'application/json'}
                                    )
            data['response'] = []
            for date_item in response.json()['calendar']['days']['day']:
                date_item['date'] = date_item['date'].replace("-", "/")
                data['response'].append(date_item)
        except Exception as e:
            status = 500
            data['response'] = str(e)
        if status < 400:
            status_detail = 'success'
        else:
            status_detail = 'fail'

        return status, json.dumps({'status': status_detail, 'data': data})

    def trading_day_status(self, date="today"):
        data = {
            'request': 'trading_day_status'
        }
        if date.lower() == "today":
            status = 200
            date = datetime.now(self.time_zone)
        else:
            try:
                date = datetime.strptime(date, "%Y/%m/%d")
                status = 200
            except Exception as e:
                status = 400
                data['response'] = "{} is not in correct format : {}".format(date, str(e))

        if status == 200:
            request_year = date.strftime("%Y")
            request_month = date.strftime("%m")

            try:
                status = 200
                response_status, response = self.trading_dates_of_month(request_year, request_month)
                if response_status == 200:
                    for date_item in json.loads(response)['data']['response']:
                        if date_item['date'] == date.strftime("%Y/%m/%d"):
                            if date_item['status'] == "closed":
                                status = 300
                            else:
                                status = 200
                            data['response'] = date_item
                            break
                        else:
                            status = 404
                            data['response'] = "{} not found".format(date.strftime("%Y-%m-%d"))
                else:
                    status = response_status
                    data['response'] = json.loads(response)['data']['response']
            except Exception as e:
                status = 501
                data['response'] = str(e)
        if status < 400:
            status_detail = 'success'
        else:
            status_detail = 'fail'

        return status, json.dumps({'status': status_detail, 'data': data})

    def last_trading_date(self, date="today"):
        data = {
            'request': 'last_trading_date'
        }
        if date == "today":
            status = 200
            date = datetime.now(self.time_zone)
            current_time = int(date.strftime("%H%M%S%f"))
        else:
            current_time = 1
            try:
                date = datetime.strptime(date, "%Y/%m/%d")
                status = 200
            except Exception as e:
                status = 400
                data['response'] = str(e)

        if status == 200:
            try:
                response_status, response = self.trading_day_status(date.strftime("%Y/%m/%d"))
                if response_status < 400:
                    if json.loads(response)['data']['response']['status'] == 'open':
                        market_close_time = int("".join(json.loads(response)['data']['response']['open']['end'].split(':'))) * 100000000
                    else:
                        market_close_time = 160000000000

                    if current_time >= market_close_time:
                        request_date = date
                    else:
                        request_date = date - timedelta(days=1)

                    for i in range(5):
                        try:
                            status = 200
                            response_status, response = self.trading_day_status((request_date - timedelta(days=i)).strftime("%Y/%m/%d"))

                            if response_status == 200:
                                if json.loads(response)['data']['response']['status'] == 'open':
                                    status = status
                                    data['response'] = json.loads(response)['data']['response']
                                    break
                                else:
                                    pass
                        except Exception as e:
                            status = 502
                            data['response'] = str(e)
                            break
            except Exception as e:
                status = 503
                status = status
                data['response'] = str(e)
        if status < 400:
            status_detail = 'success'
        else:
            status_detail = 'fail'

        return status, json.dumps({'status': status_detail, 'data': data})

    def next_trading_date(self, date="today"):
        data = {
            'request': 'next_trading_date'
        }
        if date == "today":
            status = 200
            date = datetime.now(self.time_zone)
            current_time = int(date.strftime("%H%M%S%f"))
        else:
            current_time = 235900000000
            try:
                date = datetime.strptime(date, "%Y/%m/%d")
                status = 200
            except Exception as e:
                status = 400
                data['response'] = str(e)

        if status == 200:
            try:
                response_status, response = self.trading_day_status(date.strftime("%Y/%m/%d"))
                if response_status < 400:
                    if json.loads(response)['data']['response']['status'] == 'open':
                        market_start_time = int("".join(json.loads(response)['data']['response']['open']['start'].split(':'))) * 100000000
                    else:
                        market_start_time = 93000000000

                    if current_time <= market_start_time:
                        request_date = date
                    else:
                        request_date = date + timedelta(days=1)

                    for i in range(5):
                        try:
                            status = 200
                            response_status, response = self.trading_day_status(
                                (request_date + timedelta(days=i)).strftime("%Y/%m/%d"))
                            if response_status == 200:
                                if json.loads(response)['data']['response']['status'] == 'open':
                                    status = status
                                    data['response'] = json.loads(response)['data']['response']
                                    break
                                else:
                                    pass
                        except Exception as e:
                            status = 504
                            data = str(e)
                            break
            except Exception as e:
                status = 505
                data['response'] = str(e)

        if status == 200:
            status_detail = 'success'
        else:
            status_detail = 'fail'

        return status, json.dumps({'status': status_detail, 'data': data})
