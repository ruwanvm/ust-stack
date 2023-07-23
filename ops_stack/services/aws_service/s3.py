import json
import os
from os.path import split, join

import boto3
from botocore.exceptions import ClientError


class S3:
    def __init__(self, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY):
        try:
            self.s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
            self.s3_connected = True
            self.s3_details = "S3 connection success"
        except Exception as e:
            self.s3_connected = False
            self.s3_details = "S3 connection fail : {}".format(str(e))

    def upload_file(self, file_name, bucket, bucket_location='root', object_name=None, remove=False,
                    directory=os.getcwd()):
        data = {
            'request': 's3_upload_file'
        }
        file = join(directory, file_name)
        if object_name is None:
            object_name = file_name
        if self.s3_connected:
            try:
                if bucket_location == 'root':
                    s3_key = object_name
                else:
                    s3_key = "{}/{}".format(bucket_location, object_name)
                self.s3_client.upload_file(file, bucket, s3_key)
                if self.check_file_availability(file_name=object_name, bucket=bucket,
                                                bucket_location=bucket_location):
                    status = 200
                    data['response'] = {'file': s3_key, 'uploaded': True}
                else:
                    status = 404
                    data['response'] = {'file': s3_key, 'uploaded': False}
                if remove:
                    os.remove(file)
            except Exception as e:
                status = 501
                data['response'] = str(e)
        else:
            status = 801
            data['response'] = self.s3_details

        if status == 200:
            status_detail = 'success'
        else:
            status_detail = 'fail'

        return status, json.dumps({'status': status_detail, 'data': data})

    def download_file(self, file_name, bucket, bucket_location='root', directory=os.getcwd()):
        data = {
            'request': 's3_download_file'
        }
        if bucket_location == 'root':
            s3_key = file_name
        else:
            s3_key = "{}/{}".format(bucket_location, file_name)
        if self.s3_connected:
            try:
                if self.check_file_availability(file_name=file_name, bucket=bucket,
                                                bucket_location=bucket_location):
                    self.s3_client.download_file(bucket, s3_key, join(directory, file_name))
                    status = 200
                    data['response'] = {'file': join(directory, file_name), 'downloaded': True}
                else:
                    status = 404
                    data['response'] = "File not available"
            except Exception as e:
                status = 502
                data['response'] = str(e)
        else:
            status = 802
            data['response'] = self.s3_details

        if status == 200:
            status_detail = 'success'
        else:
            status_detail = 'fail'

        return status, json.dumps({'status': status_detail, 'data': data})

    def create_presigned_url(self, file_name, bucket, bucket_location='root', expiration=3600):
        data = {
            'request': 'create_presigned_url'
        }
        if bucket_location == 'root':
            s3_key = file_name
        else:
            s3_key = "{}/{}".format(bucket_location, file_name)
        if self.s3_connected:
            try:
                status = 200
                parameters = {'Bucket': bucket, 'Key': s3_key}
                if self.check_file_availability(file_name=file_name, bucket=bucket,
                                                bucket_location=bucket_location):
                    status = 200
                    data['response'] = {'file': file_name,
                                        'presigned_url': self.s3_client.generate_presigned_url('get_object',
                                                                                               Params=parameters,
                                                                                               ExpiresIn=expiration)}
                else:
                    status = 404
                    data['response'] = "File not available"
            except Exception as e:
                status = 503
                data['response'] = str(e)
        else:
            status = 803
            data['response'] = self.s3_details

        if status == 200:
            status_detail = 'success'
        else:
            status_detail = 'fail'

        return status, json.dumps({'status': status_detail, 'data': data})

    def check_file_availability(self, file_name, bucket, bucket_location='root'):
        if bucket_location == 'root':
            s3_key = file_name
        else:
            s3_key = "{}/{}".format(bucket_location, file_name)
        if self.s3_connected:
            try:
                self.s3_client.head_object(Bucket=bucket, Key=s3_key)
            except ClientError as e:
                return int(e.response['Error']['Code']) != 404
            return True
        return False
