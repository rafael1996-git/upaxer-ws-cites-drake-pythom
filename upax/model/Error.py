from datetime import datetime

class Error:

    def __init__(self, id_service, status, source, title, detail):
        """
        Create the response of the Method execution
        :param code (str): Response code generated
        :param success (boolean):
        :param message:
        """
        self.id_service = id_service
        self.status = status
        self.source = source
        self.title = title
        self.detail = detail
        self.response = None

    def create(self):
        self.response = {
            'idService': self.id_service,
            'code': self.status,
            'source': {
                'pointer': self.source
            },
            'title': self.title,
            'detail': self.detail
        }
        return self.response
