import base64
import email
import json
import os
import time
from os.path import basename, join

from googleapiclient.discovery import build
from oauth2client import file, client, tools
from httplib2 import Http
import mimetypes
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.mime.multipart import MIMEMultipart


class Gmail:
    def __init__(self, gmail_credentials_file, gmail_token_file, gmail_scopes="readonly,send"):
        self.gmail_connected = False
        scopes = []
        gmail_scope_endpoint = "https://www.googleapis.com/auth/gmail"
        for gmail_scope in gmail_scopes.split(","):
            scopes.append("{}.{}".format(gmail_scope_endpoint, gmail_scope))
        if scopes:
            try:
                store = file.Storage(gmail_token_file)
                creds = store.get()
                if not creds or creds.invalid:
                    flow = client.flow_from_clientsecrets(gmail_credentials_file, scopes)
                    creds = tools.run_flow(flow, store)
                self.gmail_service = build('gmail', 'v1', http=creds.authorize(Http()))
                self.gmail_connected = True
                self.gmail_details = "gmail service initialized"
            except Exception as e:
                self.gmail_details = "gmail initializing fail : {}".format(str(e))
        else:
            self.gmail_details = "invalid gmail scopes : {}".format(gmail_scopes)

    def query_emails(self, query, label_ids=None, max_results=None):
        """Query to filter out emails

        Args:
            :param query: query to filter mails (subject:sybject to:me)
            :param label_ids: ids of labels
            :param max_results: maximum number of outputs required
        """
        data = {
            'request': 'gmail-query_emails'
        }
        if self.gmail_connected:
            if label_ids is None:
                label_ids = []
            else:
                label_ids = label_ids.upper()
                label_ids = label_ids.split(",")
            try:
                response = self.gmail_service.users().messages().list(userId="me", q=query,
                                                                      labelIds=label_ids,
                                                                      maxResults=max_results).execute()
                messages = []
                if 'messages' in response:
                    messages.extend(response['messages'])

                while 'nextPageToken' in response:
                    if len(messages) >= max_results:
                        break
                    page_token = response['nextPageToken']
                    response = self.gmail_service.users().messages().list(userId="me", q=query,
                                                                          labelIds=label_ids,
                                                                          pageToken=page_token).execute()
                    messages.extend(response['messages'])
                status = 200
                data['response'] = messages
            except Exception as e:
                status = 501
                data['response'] = str(e)
        else:
            status = 503
            data['response'] = self.gmail_details

        if status == 200:
            status_detail = 'success'
        else:
            status_detail = 'fail'
        return status, json.dumps({'status': status_detail, 'data': data})

    def send_email(self, to, subject, content, cc=None, bcc=None, attachments=None):
        """Send mail
        Args:
            :param to: email address or receiver.
            comma separated email addresses for more than one address eg: john@example.com, peter@example.com
            :param subject: subject of the mail
            :param content: content of the mail
            :param cc: email address to whom carbon copy should be sent.
            comma separated email addresses for more than one address
            :param bcc: email address to whom blind carbon copy should be sent.
            comma separated email addresses for more than one address
            :param attachments: comma separated Files to send as attachments

        """
        data = {
            'request': 'send_email'
        }
        if self.gmail_connected:
            try:
                if attachments is None:
                    attachments = []
                else:
                    attachments = attachments.split(",")
                message = MIMEMultipart()
                message['to'] = to
                message['from'] = "me"
                message['subject'] = subject
                message['cc'] = cc
                message['bcc'] = bcc
                msg = MIMEText(content, "html")
                message.attach(msg)
                for attachment in attachments:
                    content_type, encoding = mimetypes.guess_type(attachment)
                    if content_type is None or encoding is not None:
                        content_type = 'application/octet-stream'
                    main_type, sub_type = content_type.split('/', 1)
                    fp = open(attachment, 'rb')
                    msg = MIMEBase(main_type, sub_type)
                    msg.set_payload(fp.read())
                    fp.close()
                    filename = basename(attachment)
                    msg.add_header('Content-Disposition', 'attachment', filename=filename)
                    message.attach(msg)
                    encoders.encode_base64(msg)
                raw_msg = {'raw': (base64.urlsafe_b64encode(message.as_bytes()).decode())}
                message = (self.gmail_service.users().messages().send(userId="me", body=raw_msg).execute())
                status = 200
                data['response'] = {'send': True, 'details': message}
            except Exception as e:
                status = 502
                data['response'] = {'send': False, 'error': str(e)}
        else:
            status = 503
            data['response'] = self.gmail_details

        if status == 200:
            status_detail = 'success'
        else:
            status_detail = 'fail'
        return status, json.dumps({'status': status_detail, 'data': data})

    def wait_reply(self, query):
        data = {
            'request': 'wait_mail_reply'
        }
        if self.gmail_connected:
            try:
                status, send_mail_ids = self.query_emails(query=query, label_ids='SENT')
                if status == 200:
                    send_mail_ids = json.loads(send_mail_ids)['data']['response']
                    if send_mail_ids:
                        second = 0
                        waiting_reply = True
                        while waiting_reply:
                            status, reply_mail_ids = self.query_emails(query=query)
                            if status == 200:
                                reply_mail_ids = json.loads(reply_mail_ids)['data']['response']
                                m, s = divmod(second, 60)
                                h, m = divmod(m, 60)
                                print("Waiting for reply : {:d}:{:02d}:{:02d}".format(h, m, s), end="\r")
                                if len(reply_mail_ids) == len(send_mail_ids) + 1:
                                    print('Reply Received in : ')
                                    for send_mail in send_mail_ids:
                                        reply_mail_ids.remove(send_mail)
                                    print(reply_mail_ids)
                                    waiting_reply = False
                                    data['response'] = {'send': send_mail_ids, 'reply': reply_mail_ids}
                                else:
                                    time.sleep(1)
                                    second = second + 1
                            else:
                                waiting_reply = False
                                data['response'] = "Query replies failed : {}".format(
                                    json.loads(reply_mail_ids)['data']['response'])
                                print("Query mails failed")
                    else:
                        data['response'] = "No mails send with {}".format(query)
                        print("Send mails not found")
                else:
                    data['response'] = "Query replies failed : {}".format(json.loads(send_mail_ids)['data']['response'])
                    print("Query mails failed")
            except Exception as e:
                status = 502
                data['response'] = str(e)
        else:
            status = 503
            data['response'] = self.gmail_details

        if status == 200:
            status_detail = 'success'
        else:
            status_detail = 'fail'
        return json.dumps({'status': status_detail, 'data': data})

    def get_message_as_string(self, mail_id):
        """Get first 200 characters of a mail

        :param mail_id: mail_id to get the message
        :return: json object of first 200 characters of the mail
        """
        data = {
            'request': 'get_mail_as_string'
        }
        if self.gmail_connected:
            try:
                message = self.gmail_service.users().messages().get(userId="me", id=mail_id).execute()
                content = str(message['snippet'])
                status = 200
                data['response'] = content
            except Exception as e:
                status = 503
                data['response'] = str(e)
        else:
            status = 503
            data['response'] = self.gmail_details

        if status == 200:
            status_detail = 'success'
        else:
            status_detail = 'fail'
        return status, json.dumps({'status': status_detail, 'data': data})

    def get_mime_message(self, mail_id):
        """Get all email content

        :param mail_id:
        :return: json object of mail content
        """
        data = {
            'request': 'get_mail_as_mime_text'
        }
        if self.gmail_connected:
            try:
                status = 200
                message = self.gmail_service.users().messages().get(userId="me", id=mail_id, format='raw').execute()
                msg_str = base64.urlsafe_b64decode(message['raw']).decode()
                mime_msg = email.message_from_string(msg_str)
                data['response'] = []
                if mime_msg.is_multipart():
                    for payload in mime_msg.get_payload():
                        data['response'].append(payload.get_payload().replace("\r\n", ""))
                else:
                    data['response'].append(mime_msg.get_payload().replace("\r\n", ""))
            except Exception as e:
                status = 504
                data['response'] = str(e)
        else:
            status = 503
            data['response'] = self.gmail_details

        if status == 200:
            status_detail = 'success'
        else:
            status_detail = 'fail'
        return status, json.dumps({'status': status_detail, 'data': data})

    def download_attachments(self, mail_id, directory=os.getcwd(), prefix=""):
        """download mail attachments

        Args:
            mail_id: Google mail id of the received mail
            directory: Directory where attachments downloaded
            prefix: Prefix to append to attachments
        """
        data = {
            'request': 'download_mail_attachments'
        }
        try:
            if self.gmail_connected:
                status = 200
                message = self.gmail_service.users().messages().get(userId="me", id=mail_id).execute()
                data['response'] = {'mail_id': message['id'], 'attachments': []}
                if 'parts' in message['payload']:
                    for part in message['payload']['parts']:
                        if part['filename']:
                            attachment_object = {'attachment_name': part['filename']}
                            if 'data' in part['body']:
                                att_data = part['body']['data']
                            else:
                                att_id = part['body']['attachmentId']
                                att = self.gmail_service.users().messages().attachments().get(userId="me",
                                                                                              messageId=mail_id,
                                                                                              id=att_id).execute()
                                att_data = att['data']
                            file_data = base64.urlsafe_b64decode(att_data.encode('UTF-8'))
                            with open(join(directory, prefix + part['filename']), 'wb') as f:
                                f.write(file_data)
                                attachment_object['attachment_downloaded'] = True
                                attachment_object['attachment_downloaded_path'] = join(directory, prefix + part['filename'])
                            data['response']['attachments'].append(attachment_object)
                            status = 200
                else:
                    status = 404
                    data['response'] = 'attachments not found'
            else:
                status = 503
                data['response'] = self.gmail_details
        except Exception as e:
            status = 505
            data['response'] = str(e)

        if status == 200:
            status_detail = 'success'
        else:
            status_detail = 'fail'
        return status, json.dumps({'status': status_detail, 'data': data})
