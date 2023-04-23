import os

bucket_name = os.environ['BUCKET_NAME']
file = os.environ['CONFIG_FILE']

path = '/gd/visit'
path2 = '/gd/user'

#DEV
#bucket_name = 'upaxer-serverless-api'
#file = 'config_sls/upx_sls_config.json'
#path = 'visit'

#QA
#bucket_name = 'upaxer-serverless-api-qa'
#file = 'config_sls/upx_sls_config.json'
#path = 'dates'

#PROD
#bucket_name = 'ups-sls-api'
#file = 'config_sls/upx_sls_config.json'
#path = 'dates'