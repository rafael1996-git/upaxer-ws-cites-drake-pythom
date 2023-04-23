from common.Utils import Utils as utils
from common.Constants import IMPUTABLE
import datetime
from dateutil import tz

class Reprogramming:

    def __init__(self, body):
        self.body = body

    def build(self):
        result = {
            'visitDate': int(datetime.datetime.timestamp(datetime.datetime.strptime(self.body['FECHAVISITA'], '%d/%m/%Y %H:%M:%S') + datetime.timedelta(hours=5))) if self.body['FECHAVISITA'] is not None else None,
            'upaxId': str(self.body['FCUSUARIO']),
            'upaxName': self.body['USUARIO'],
            'statusField': str(self.body['FIIDESTATUS']),
            'imputable': IMPUTABLE,
            'description': utils.set_status(self.body['FIIDESTATUS']),
            'comments': self.body['COMENTARIO_AUDITORIA']
        }
        return result
