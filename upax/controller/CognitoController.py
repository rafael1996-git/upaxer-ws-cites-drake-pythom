import boto3
import hashlib
import hmac
import base64
from upax.config.RemoteConfig import RemoteConfig


class CognitoController:

    def __init__(self):
        config = RemoteConfig().get_config()['cognito']['generic']
        self.poolId = config['poolId']
        self.clientId = config['clientId']
        self.clientSecret = config['clientSecret']
        self.client = boto3.client('cognito-idp')

    def create_user(self, username, password):
        try:
            data = self.client.sign_up(
                ClientId=self.clientId,
                Username=username,
                Password=password
            )
            data = self.client.admin_confirm_sign_up(
                UserPoolId=self.poolId,
                Username=username
            )
            response = {
                'hasError': False,
                'response': data
            }
        except self.client.exceptions.UsernameExistsException as e:
            raise Exception({'message': 'Ocurrio un error con Cognito: ' + str(e), 'code': 'UPX604'})
        except Exception as e:
            raise Exception({'message': 'Ocurrio un error con Cognito: ' + str(e), 'code': 'UPX604'})
        return response

    def generate_auth_token(self, username, password):
        try:
            data = self.client.admin_initiate_auth(
                UserPoolId=self.poolId,
                ClientId=self.clientId,
                AuthFlow='ADMIN_NO_SRP_AUTH',
                AuthParameters={
                    'USERNAME': username,
                    'PASSWORD': password
                }
            )
            response = {
                'hasError': False,
                'response': data
            }
        except Exception as e:
            raise Exception({'message': 'Ocurrio un error con Cognito: ' + str(e), 'code': 'UPX604'})
        return response

    def refresh_token(self, username, token):
        try:
            data = self.client.admin_initiate_auth(
                UserPoolId=self.poolId,
                ClientId=self.clientId,
                AuthFlow='REFRESH_TOKEN_AUTH',
                AuthParameters={
                    'REFRESH_TOKEN': token,
                    'SECRET_HASH': self.get_secret_hash(username=username, clientSecret=self.clientSecret, clientId=self.clientId),
                    'DEVICE_KEY': ''
                }
            )
            response = {
                'hasError': False,
                'response': data
            }
        except Exception as e:
            raise Exception({'message': 'Ocurrio un error con Cognito: ' + str(e), 'code': 'UPX604'})
        return response

    @staticmethod
    def get_secret_hash(username, clientId, clientSecret):
        msg = username + clientId
        dig = hmac.new(str(clientSecret).encode('utf-8'), msg=str(msg).encode('utf-8'),
                       digestmod=hashlib.sha256).digest()
        d2 = base64.b64encode(dig).decode()
        return d2