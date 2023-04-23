import boto3
import json
import os
from datetime import date, datetime


def req_s3(data):
    key = 'request/cites/'
    upload_s3(data, key)


def res_s3(data):
    key = 'response/cites/'
    upload_s3(data, key)


def upload_s3(data, folder):
    s3 = boto3.resource('s3')
    bucket = os.environ['BUCKET_LOG']
    key = folder + str(date.today()) + '/' + str(datetime.now()) + '.json'
    s3.Bucket(bucket).put_object(Key=key, Body=json.dumps(data))
