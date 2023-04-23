from upax.controller.CognitoController import CognitoController
from datetime import datetime

SUCCESS_CODE = 'UPX200'
SUCCESS_MESSAGE = 'Ok'
ERROR_CODE = 'UPX500'

class TokenService:

    def __init__(self, path, parameters):
        self.path = path
        self.parameters = parameters

    def create_user(self):
        try:
            username = self.parameters['username']
            password = self.parameters['password']
            response = CognitoController().create_user(username=username, password=password)
            return response
        except Exception as e:
            return str(e)

    def generate_token(self):
        try:
            username = self.parameters['username']

            password = self.parameters['password']
            response = CognitoController().generate_auth_token(username=username, password=password)
            if response['hasError']:
                return Error(status=ERROR_CODE, source=self.path, title='Authentication Error',
                             detail=response['response'])
            else:
                data = {
                    'IdToken': response['response']['AuthenticationResult']['IdToken'],
                    'TokenType': response['response']['AuthenticationResult']['TokenType'],
                    'ExpiresIn': response['response']['AuthenticationResult']['ExpiresIn']
                }
                return Response(status=SUCCESS_CODE, message=SUCCESS_MESSAGE, data=data)
        except Exception as e:
            if hasattr(e, 'args') and isinstance(e.args[0], dict):
                if 'code' in e.args[0]:
                    return Error(status=e.args[0]['code'], source=self.path, title='Error in service', detail=e.args[0]['message'])
            return Error(status=ERROR_CODE, source=self.path, title='Error in service', detail=str(e))

    def refresh_token(self):
        try:
            username = self.parameters['username']
            token = self.parameters['token']
            response = CognitoController().refresh_token(username=username, token=token)
            if response['hasError']:
                return Error(status=ERROR_CODE, source=self.path, title='Re-authentication Error',
                             detail=response['response'])
            else:
                return Response(status=SUCCESS_CODE, message=SUCCESS_MESSAGE, data=response['response'])
        except Exception as e:
            return Error(status=ERROR_CODE, source=self.path, title='Error in service', detail=str(e))


class Response:

    def __init__(self, status, data=None, message=None):
        """
        Create the response of the Method execution
        :param code (str): Response code generated
        :param success (boolean):
        :param message:
        """
        self.status = status
        self.message = message
        self.data = data
        self.response = None

    def create(self):
        self.response = {
            'timestamp': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            'code': self.status,
            'message': self.message,
            'response': self.data
        }
        return self.response

class Error:

    def __init__(self, status, source, title, detail):
        """
        Create the response of the Method execution
        :param code (str): Response code generated
        :param success (boolean):
        :param message:
        """
        self.status = status
        self.source = source
        self.title = title
        self.detail = detail
        self.response = None

    def create(self):
        self.response = {
            'timestamp': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            'code': self.status,
            'source': self.source,
            'title': self.title,
            'message': self.detail
        }
        return self.response