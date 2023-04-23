
import boto3
import json
from common.Properties import bucket_name, file


class RemoteConfig:

    def __init__(self):
        self.client = boto3.client('s3')

    def get_config(self):
        return json.loads(self.client.get_object(Bucket=bucket_name, Key=file)['Body'].read().decode())
