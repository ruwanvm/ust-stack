import json
import os
from os.path import join, isfile

from jira import JIRA


class Jira:
    def __init__(self, host, username, token):
        try:
            options = {'server': host}
            self.jira_service = JIRA(options, basic_auth=(username, token))
            self.jira_connected = True
            self.jira_details = 'JIRA connection success'
        except Exception as e:
            self.jira_connected = False
            self.jira_details = 'JIRA connection fail : {}'.format(str(e))

    def search_issues(self, jql, max_results=50):
        data = {
            'request': 'jira-search_issues'
        }
        if self.jira_connected:
            try:
                tickets = self.jira_service.search_issues(jql, maxResults=max_results)
                data['response'] = []
                for ticket in tickets:
                    jira_item = {'id': ticket.key, 'summary': ticket.fields.summary}
                    data['response'].append(jira_item)
                status = 200
            except Exception as e:
                status = 501
                data['response'] = 'Error searching JIRA issues : {}'.format(str(e))
        else:
            status = 505
            data['response'] = self.jira_details

        if status == 200:
            status_detail = 'success'
        else:
            status_detail = 'fail'
        return status, json.dumps({'status': status_detail, 'data': data})

    def get_issue_attributes(self, issue_id, attributes="*"):
        data = {
            'request': 'jira-get_issue_attributes'
        }
        if self.jira_connected:
            try:
                ticket = self.jira_service.issue(issue_id)
                attribute_dict = {
                    'title': ticket.fields.summary,
                    'description': ticket.fields.description,
                    'status': ticket.fields.status,
                    'environment': ticket.fields.environment,
                    'assignee': ticket.fields.assignee,
                    'reporter': ticket.fields.reporter,
                    'targetststem': ticket.fields.customfield_10201,
                    'fixedbinaryversion': ticket.fields.customfield_10300,
                    'approver': ticket.fields.customfield_11420,
                    'validator': ticket.fields.customfield_11439,
                    'resolver': ticket.fields.customfield_11442,
                    'fixVersions': ticket.fields.fixVersions,
                    'created': ticket.fields.created,
                    'priority': ticket.fields.priority,
                    'issuelinks': ticket.fields.issuelinks,
                    'watches': ticket.fields.watches,
                    'comment': ticket.fields.comment.comments
                }
                if attributes == "*":
                    attributes = ",".join(attribute_dict.keys())
                data['response'] = {'issue_id': issue_id, 'attributes': {}}
                for attribute in attributes.split(","):
                    if attribute.strip() in attribute_dict:
                        data['response']['attributes'][attribute] = {'available': True,
                                                                     'value': str(attribute_dict.get(attribute))}
                    else:
                        data['response']['attributes'][attribute] = {'available': False}
                status = 200
            except Exception as e:
                status = 505
                data['response'] = str(e)
        else:
            status = 505
            data['response'] = self.jira_details

        if status == 200:
            status_detail = 'success'
        else:
            status_detail = 'fail'
        return status, json.dumps({'status': status_detail, 'data': data})

    def create_new_issue(self, project, summary, description, issue_type='Task', assignee=None, attachments=None):
        data = {
            'request': 'jira-create_new_issue'
        }
        if self.jira_connected:
            try:
                status = 200
                new_issue = self.jira_service.create_issue(project=project, summary=summary,
                                                           issuetype={'name': issue_type},
                                                           description=description, assignee={'name': assignee})
                data['response'] = {'issue_id': new_issue.key}
                if attachments is not None:
                    attachment_status, attachment_details = self.add_issue_attachments(issue_id=new_issue.key,
                                                                                       attachments=attachments)
                    data['response']['attachments'] = json.loads(attachment_details)['data']['response']
            except Exception as e:
                status = 507
                data['response'] = str(e)
        else:
            status = 505
            data['response'] = self.jira_details

        if status == 200:
            status_detail = 'success'
        else:
            status_detail = 'fail'
        return status, json.dumps({'status': status_detail, 'data': data})

    def add_issue_attachments(self, issue_id, attachments=None):
        data = {
            'request': 'jira-add_issue_attachments'
        }
        if self.jira_connected:
            if attachments is not None:
                status = 303
                data['response'] = {'issue_id': issue_id, 'attachments': []}
                for attachment in attachments:
                    if isinstance(attachment, dict):
                        file_name = attachment['file_name']
                        if 'directory' in attachment:
                            file_dir = attachment['directory']
                        else:
                            file_dir = os.getcwd()
                    else:
                        file_name = attachment
                        file_dir = os.getcwd()
                    if isfile(join(file_dir, file_name)):
                        try:
                            status = 200
                            self.jira_service.add_attachment(issue=issue_id, attachment=join(file_dir, file_name))
                            attachment_item = {'file': file_name, 'attached': True}
                        except Exception as e:
                            status = 303
                            attachment_item = {'file': file_name, 'attached': False, 'error': str(e)}
                    else:
                        status = 404
                        attachment_item = {'file': file_name, 'attached': False, 'error': 'file not found'}
                    data['response']['attachments'].append(attachment_item)
            else:
                status = 406
                data['response'] = "Attachments not defined"
        else:
            status = 505
            data['response'] = self.jira_details

        if status < 400:
            status_detail = 'success'
        else:
            status_detail = 'fail'
        return status, json.dumps({'status': status_detail, 'data': data})

    def update_issue(self, issue_id, attribute, value):
        data = {
            'request': 'jira-update_issue'
        }
        if self.jira_connected:
            ticket = self.jira_service.issue(issue_id)
            data['response'] = {'issue_id': issue_id, 'attribute': attribute}
            if attribute == "assignee":
                try:
                    status = 200
                    ticket.update(assignee={'name': value})
                    data['response']['uploaded'] = True
                except Exception as e:
                    status = 508
                    data['response']['uploaded'] = False
                    data['response']['error'] = str(e)
            elif attribute == "issue_type":
                try:
                    status = 200
                    ticket.update(issuetype={'name': value})
                    data['response']['uploaded'] = True
                except Exception as e:
                    status = 508
                    data['response']['uploaded'] = False
                    data['response']['error'] = str(e)
            else:
                try:
                    status = 200
                    ticket.update(fields={attribute: value})
                    data['response']['uploaded'] = True
                except Exception as e:
                    status = 508
                    data['response']['uploaded'] = False
                    data['response']['error'] = str(e)
        else:
            status = 505
            data['response'] = self.jira_details

        if status == 200:
            status_detail = 'success'
        else:
            status_detail = 'fail'
        return status, json.dumps({'status': status_detail, 'data': data})

    def delete_issue(self, issue_id):
        data = {
            'request': 'jira-delete_issue'
        }
        if self.jira_connected:
            try:
                ticket = self.jira_service.issue(issue_id)
                status = 200
                ticket.delete()
                data['response'] = {'issue_id': issue_id, 'deleted': True}
            except Exception as e:
                status = 509
                data['response'] = {'issue_id': issue_id, 'deleted': False, 'error': str(e)}
        else:
            status = 505
            data['response'] = self.jira_details

        if status == 200:
            status_detail = 'success'
        else:
            status_detail = 'fail'
        return status, json.dumps({'status': status_detail, 'data': data})

    def add_issue_comment(self, issue_id, comment):
        data = {
            'request': 'jira-add_issue_comment'
        }
        if self.jira_connected:
            try:
                status = 200
                self.jira_service.add_comment(issue_id, comment)
                data['response'] = {'issue_id': issue_id, 'commented': True}
            except Exception as e:
                status = 510
                data['response'] = {'issue_id': issue_id, 'commented': False, 'error': str(e)}
        else:
            status = 505
            data['response'] = self.jira_details

        if status == 200:
            status_detail = 'success'
        else:
            status_detail = 'fail'
        return status, json.dumps({'status': status_detail, 'data': data})
