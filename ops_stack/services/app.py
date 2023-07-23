import configparser
import getopt
import json
import logging
import os
import random
import string
import sys
from os.path import join, isfile
import requests
import pyfiglet
from datetime import datetime, timedelta

from ops_stack.services.date_service import DateTime
from ops_stack.services.date_service.trading_calendar import TradingDays


class App:
    def __init__(self, app_config_file=None):
        try:
            self.cwd = os.getcwd()
            self.input_directory = join(self.cwd, '_inputs')
            self.output_directory = join(self.cwd, '_outputs')
            self.apps_directory = join(self.cwd, "_apps")
            self.config_directory = join(self.cwd, 'conf')
            self.log_directory = join(self.cwd, 'logs')
            self.tmp_directory = join(self.cwd, '_tmp')
            self.backup_directory = join(self.cwd, '_backups')
            if app_config_file:
                app_config_file = join(self.apps_directory, app_config_file)
                if isfile(app_config_file):
                    self.configs = configparser.ConfigParser()
                    self.configs.read(app_config_file)
                    self.job_id = self.get_unique_id()
                    self.app_name = self.configs['DEFAULT']['app_name']
                    self.app_id = self.configs['DEFAULT']['app_id']
                    self.user_data = self.app_name

                    self.log_file_name = 'UST_OPERATIONS.log'
                    self.log_file_path = join(self.log_directory, self.log_file_name)
                    logging.getLogger().setLevel(logging.INFO)
                    logging.basicConfig(filename=self.log_file_path, filemode='a',
                                        format='{} | {} | {} | %(levelname)s | %(asctime)s | %(message)s'.format(
                                            self.app_name, self.app_id, self.job_id))
                    self.status = 200
                    self.status_details = "{} Initialized".format(self.app_name)
                    self.response = "{} Initialized".format(self.app_name)
                else:
                    self.status = 404
                    self.status_details = "App config file not found"
            else:
                self.status = 405
                self.status_details = "App config file not defined"
        except Exception as e:
            self.status = 500
            self.status_details = "Error initializing App : {}".format(str(e))

    @staticmethod
    def get_unique_id(length=16):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

    def start(self):
        """
        Start a new app
        """
        if self.status == 200:
            try:
                print(pyfiglet.figlet_format(self.app_name.replace("_", " "), font="Tinker-Toy"))  # Tinker-Toy,
            finally:
                print("{} started (job id : {})".format(self.app_name, self.job_id))
                logging.info("{} (job id : {}) started".format(self.app_name, self.job_id))
                self.response = "{} (job id : {}) started".format(self.app_name, self.job_id)
        else:
            self.status = 500
            print("App could not be started : {}".format(self.status_details))
            self.response = "App could not be started : {}".format(self.status_details)

    def stop(self):
        print(self.status, self.status_details)
        if self.status == 200:
            logging.info("{} (job id : {}) stopped".format(self.app_name, self.job_id))
            self.status_details = "{} completed successfully".format(self.app_name)
            self.response = "{} completed successfully".format(self.app_name)
            self.send_message_webhook(os.getenv('OPS_WEBHOOK'),
                                      """*Task* : {} :heavy_check_mark:\n*User Data* : {}\n*Status* : {}\n*Details* : {}.""".format(
                                          self.app_name, self.user_data, self.status, self.status_details))
            sys.exit()
        elif self.status >= 400:
            self.send_message_webhook(os.getenv('OPS_WEBHOOK'),
                                      """*Task* : {} :x:\n*User Data* : {}\n*Status* : {}\n*Details* : {}.""".format(
                                          self.app_name, self.user_data, self.status, self.status_details))
            # Send message to devops webhook
            with open(join(self.log_directory, self.log_file_name), 'r') as file:
                lines_list = file.readlines()
            dev_ops_message = "\n".join(lines_list[-10:])
            self.send_message_webhook(os.getenv('DEVOPS_WEBHOOK'), dev_ops_message)
            sys.exit(self.status)
        else:
            self.send_message_webhook(os.getenv('OPS_WEBHOOK'),
                                      """*Task* : {} :warning:\n*User Data* : {}\n*Status* : {}\n*Details* : {}.""".format(
                                          self.app_name, self.user_data, self.status, self.status_details))
            sys.exit()

    @staticmethod
    def argument_parser(argv, arg_list=None):
        data = {
            'request': 'app-argument_parser'
        }
        argv = argv[1:]
        if arg_list is not None:
            status = 200
            data['response'] = "Argument Parser started"
            short_form = []
            long_form = []
            for arg in arg_list:
                if " " not in arg and arg[0] not in short_form and status == 200:
                    status = 200
                    short_form.append(arg[0])
                    long_form.append('{}='.format(arg))
                else:
                    status = 404
                    data['response'] = "invalid argument : {}".format(arg)
            if status == 200:
                short_form.append("")
                short_form = ":".join(short_form)
                try:
                    status = 303
                    data['response'] = {}
                    opts, args = getopt.getopt(argv, short_form, long_form)
                    for opt, arg in opts:
                        data['response'][opt.replace("-", "")] = arg
                        status = 200
                except getopt.GetoptError as err:
                    status = 500
                    data['response'] = "Error parsing argument : {}".format(err)
        else:
            status = 403
            data['response'] = "arg_list not defined"

        if status == 200:
            status_detail = 'success'
        else:
            status_detail = 'fail'

        return status, json.dumps({'status': status_detail, 'data': data})

    def check_trading_day_parameter(self, request):
        data = {
            'request': 'app-check_trading_day_parameter'
        }
        if self.configs['DEFAULT']['app_type'] == 'daily_operation' and self.configs['DEFAULT'][
            'app_frequency'] == 'TRADING_DAY':
            trading_calendar = TradingDays(tradier_api_key=os.getenv('TRADIER_API_KEY'))
            if request == 'last_trading_date':
                status, response = trading_calendar.last_trading_date()
            elif request == 'next_trading_date':
                status, response = trading_calendar.next_trading_date()
            else:
                status, response = trading_calendar.trading_day_status(date=request)
                if status == 200:
                    if json.loads(response)['data']['response']['status'] == 'open':
                        data['response'] = {'matching': True, 'date': json.loads(response)['data']['response']['date']}
                    else:
                        status = 605
                        data['response'] = json.loads(response)['data']['response']
                else:
                    data['response'] = json.loads(response)['data']['response']
            if status == 200 and request in ['last_trading_date', 'next_trading_date']:
                settlement_date = datetime.strptime(DateTime.today(time_format="%Y/%m/%d"), "%Y/%m/%d")
                trading_date = datetime.strptime(json.loads(response)['data']['response']['date'], "%Y/%m/%d")
                date_item, date_delta_operator, date_delta = self.configs['DEFAULT']['app_run_date'].split(" ")
                if date_delta_operator == "+":
                    settlement_trading_date = settlement_date - timedelta(days=int(date_delta))
                elif date_delta_operator == "-":
                    settlement_trading_date = settlement_date + timedelta(days=int(date_delta))
                else:
                    status = 603
                    data['response'] = f'Invalied settlement operator {date_delta_operator}'
            if status == 200 and request in ['last_trading_date', 'next_trading_date']:
                if settlement_trading_date == trading_date:
                    data['response'] = {'matching': True, 'date': trading_date.strftime("%Y/%m/%d")}
                else:
                    status = 604
                    data['response'] = {'matching': False, 'date': trading_date.strftime("%Y/%m/%d"),
                                        'settlement_date': settlement_trading_date.strftime("%Y/%m/%d")}
        else:
            status = 602
            data['response'] = 'Invalied application to check trading days'

        if status == 200:
            status_detail = 'success'
        else:
            status_detail = 'fail'
        return status, json.dumps({'status': status_detail, 'data': data})

    def log(self):
        if self.status == 200:
            try:
                logging.info("{}\n{}".format(self.status_details, json.dumps(json.loads(self.response), indent=4)))
                print(self.status_details)
            except:
                logging.info(self.status_details)
                print(self.status_details)
                logging.info(self.response)
        elif self.status != 200 and self.status < 400:
            try:
                logging.warning("{}\n{}".format(self.status_details, json.dumps(json.loads(self.response), indent=4)))
                print(self.status_details)
            except:
                logging.warning(self.status_details)
                print(self.status_details)
                logging.warning(self.response)
        else:
            try:
                logging.error("{}\n{}".format(self.status_details, json.dumps(json.loads(self.response), indent=4)))
                print(self.status_details)
            except:
                logging.error(self.status_details)
                print(self.status_details)
                logging.error(self.response)

    def info(self, json_response=None):
        if json_response:
            try:
                logging.info("{}\n{}".format(self.status_details, json.dumps(json.loads(json_response), indent=4)))
                print(self.status_details)
            except:
                logging.info(self.status_details)
                print(self.status_details)
                logging.info(json_response)
        else:
            logging.info(self.status_details)
            print(self.status_details)

    def debug(self, json_response=None):
        if json_response:
            try:
                logging.debug("{}\n{}".format(self.status_details, json.dumps(json.loads(json_response), indent=4)))
                print(self.status_details)
            except:
                logging.debug(self.status_details)
                print(self.status_details)
                logging.debug(json_response)
        else:
            logging.debug(self.status_details)
            print(self.status_details)

    def warning(self, json_response=None):
        if json_response:
            try:
                logging.warning("{}\n{}".format(self.status_details, json.dumps(json.loads(json_response), indent=4)))
                print(self.status_details)
            except:
                logging.warning(self.status_details)
                print(self.status_details)
                logging.warning(json_response)
        else:
            logging.warning(self.status_details)
            print(self.status_details)

    def error(self, json_response=None):
        if json_response:
            try:
                logging.error("{}\n{}".format(self.status_details, json.dumps(json.loads(json_response), indent=4)))
                print(self.status_details)
            except:
                logging.error(self.status_details)
                print(self.status_details)
                logging.error(json_response)
        else:
            logging.error(self.status_details)
            print(self.status_details)

    def critical(self, json_response=None):
        if json_response:
            try:
                logging.critical("{}\n{}".format(self.status_details, json.dumps(json.loads(json_response), indent=4)))
                print(self.status_details)
            except:
                logging.critical(self.status_details)
                print(self.status_details)
                logging.critical(json_response)
        else:
            logging.critical(self.status_details)
            print(self.status_details)

    @staticmethod
    def send_message_webhook(webhook_url, message):
        message = {'text': message}
        response = requests.post(webhook_url, data=json.dumps(message), headers={'Content-Type': 'application/json'})
        if response.status_code != 200:
            logging.error("Request to slack returned an error {}, the response is:\n{}".format(response.status_code,
                                                                                               response.text))
            raise ValueError()
