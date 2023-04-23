from datetime import datetime
from upax.controller.LogController import res_s3


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

    def body(self):
        res_s3(self.data)
        return self.data
