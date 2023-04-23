from common.Utils import Utils as utils
import datetime
from dateutil import tz


class VisitInfo:

    def __init__(self, body):
        self.body = body

    def build(self):
        result = {
            'idService': self.body['FIIDSERVICE'],
            'registerType': self.body['FIIDREGISTERTYPE'],
            'priority': self.body['FIIDPRIORITY'],
            'requestStatus': self.body['FIESTATUS'],

            #'progamationDate': self.body['FECHAPROGRAMACION'],
            'progamationDate':
                int(datetime.datetime.timestamp(
                datetime.datetime.strptime(self.body['FECHAPROGRAMACION'], '%d/%m/%Y %H:%M:%S') + datetime.timedelta(
                    hours=5))) if self.body['FECHAPROGRAMACION'] is not None else None,

            'latitud': self.body["FNLATITUD"],
            'longitud': self.body["FNLONGITUD"],

            'initValidationDate':
                int(datetime.datetime.timestamp(
                datetime.datetime.strptime(self.body['FECHAREGISTRO'], '%d/%m/%Y %H:%M:%S') + datetime.timedelta(
                    hours=5))) if self.body['FECHAREGISTRO'] is not None else None,
            'endValidationDate':
                int(datetime.datetime.timestamp(
                datetime.datetime.strptime(self.body['FECHAVISITA'], '%d/%m/%Y %H:%M:%S') + datetime.timedelta(
                    hours=5))) if self.body['FECHAVISITA'] is not None else None,

            #'initValidationDate': self.body['FECHAREGISTRO'],
            #'endValidationDate': self.body['FECHAVISITA'],



            'rejected': {
                'imputable': self.body['FCATTRIBUTETYPE'],
                'responsable': self.body['RESPONSABLE'],
                'reason': self.body['FCDECLINETYPE'],
                'comments': self.body['FCDESCRIPTION'],
                'refusalDate': int(datetime.datetime.timestamp(datetime.datetime.strptime(self.body['FECHARECHAZO'], '%d/%m/%Y %H:%M:%S') + datetime.timedelta(hours=5))) if self.body['FECHARECHAZO'] is not None else None,
            },
            'projectId': self.body['FIIDPROYECTO'],
            'projectName': self.body['NOMBREPROYECTO'],
            'responsable': {
                'name': self.body['NOMBRE'],
                'pLastName': self.body['FCAPELLIDOPATERNO'],
                'mLastName': self.body['FCAPELLIDOMATERNO'],
                'phoneNumber': self.body['TELEFONO'],
                'email': self.body['FCCORREO']
            },
            'location': {
                'id': self.body['FIIDUBICACION'],
                'name': self.body['NOMBREUBICACION'],
                'visit': {
                    'id': self.body['FIIDASIGNACION'],
                    'visitDate': int(datetime.datetime.timestamp(datetime.datetime.strptime(self.body['FECHA_VISITA'], '%d/%m/%Y %H:%M:%S') + datetime.timedelta(hours=5))) if self.body['FECHA_VISITA'] is not None else None,
                    'upaxId': str(self.body['FCUSUARIO']),
                    'upaxName': self.body['USUARIO'],
                    'status': self.body['FIIDESTATUS'],
                    'initDate': None,
                    'endDate': None
                }
            },
            'report': list()
        }
        return result
