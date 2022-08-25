import io
import json
import boto3
from flask import current_app


class AwsS3Handler:
    client = None
    #resource = None
    bucket = None


    def __init__(self, bucket):
        self.bucket = bucket
        self.client = boto3.client('s3')


    def __del__(self):
        pass


    def get_data(self, path, data_type='raw'):
        s3_data = self.client.get_object(Bucket=self.bucket, Key=path)
        raw_data = s3_data['Body'].read()
        if data_type == 'raw':
            return raw_data

        str_data = s3_data['Body'].read().decode('utf-8')
        if data_type == 'json':
            dict_data = json.loads(str_data)
            return dict_data

        return str_data


    def upload(self, blob, path, mimetype=None):
        res = self.client.put_object(
            Body = blob,
            #Body = file_strage.stream.read(),
            #Body = io.BufferedReader(file_strage).read(),
            Bucket = self.bucket,
            ContentType = mimetype,
            Key = path
        )
        return res


    def delete(self, path):
        res = self.client.delete_object(
            Bucket = self.bucket,
            Key = path
        )
        return res
