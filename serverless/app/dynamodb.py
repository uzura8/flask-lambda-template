import os
import boto3

IS_LOCAL = bool(os.environ.get('IS_LOCAL'))

if IS_LOCAL:
    dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
else:
    dynamodb = boto3.resource('dynamodb')
