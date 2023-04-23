import boto3
import json
from common.Constants import AWS_REGION, SECRETS_MANAGER


def get_secret(secret_name):
    client = boto3.session.Session().client(service_name=SECRETS_MANAGER, region_name=AWS_REGION)
    try:
        value = client.get_secret_value(SecretId=secret_name)
        return json.loads(value['SecretString'])
    except ValueError as e:
        print(e)