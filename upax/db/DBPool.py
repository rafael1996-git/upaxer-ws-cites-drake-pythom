import boto3
import json
import cx_Oracle

from bson import json_util
import os
from common.Secret import get_secret

oracle_Types = {
    'cursor': cx_Oracle.CURSOR,
    'numeric': cx_Oracle.NUMBER,
    'string': cx_Oracle.STRING
}

class DBPool():

    def __init__(self):

        self.db_info = get_secret(os.environ['SECRET_ORACLE'])
        self.server = self.db_info['server']
        self.port = self.db_info['port']
        self.service = self.db_info['service']
        self.user = self.db_info['user']
        self.password = self.db_info['password']

        connection = self.user + "/" + self.password + "@" + self.server + ":" + str(self.port) + "/" + self.service
        try:
            self.conn = cx_Oracle.connect(connection)
        except Exception as e:
            raise Exception({'message': 'Error de conexión con OracleDB', 'code': 'UPX602'})
        self.cursor = self.conn.cursor()

    def is_alive(self):
        self.cursor.execute("select 1 from DUAL")
        if (self.cursor.fetchall()):
            return True
        else:
            return False


    def execute(self, method, type, name, params = None):

        db_dto = {}
        data = []

        if (method == 'FN'):
            try:
                db_execute = self.cursor.callfunc(name, oracle_Types[type],
                                                  keywordParameters=params) if params != None else self.cursor.callfunc(
                    name, oracle_Types[type])
                if type == 'cursor':
                    columns = [field[0] for field in db_execute.description]
                    rows = db_execute.fetchall()
                    data = [dict(zip(columns, row)) for row in rows]
                    for d in data:
                        for key, value in d.items():
                            if isinstance(d[key], cx_Oracle.LOB):
                                d[key] = json.loads(str(value))
                    db_dto = {
                        "hasError": False,
                        "data": json.dumps(data, default=json_util.default)
                        #"data": json.dumps(data)
                    }
                else:
                    db_dto = {
                        "hasError": False,
                        "data": db_execute
                    }
            except Exception as e:
                raise Exception({'message': 'Ocurrio un error interno en OracleDB: ' + str(e), 'code': 'UPX603'})
            self.conn.close()
            return db_dto
        elif (method == 'SP'):
            result = self.cursor.var(oracle_Types[type])
            params.append(result)
            self.conn.close()
            return self.cursor.callproc(name, params)

    def mul_execute(self, method, type, name, params = None):
        db_dto = {}
        data = []

        if (method == 'FN'):
            try:
                db_execute = self.cursor.callfunc(name, oracle_Types[type],
                                                  keywordParameters=params) if params != None else self.cursor.callfunc(
                    name, oracle_Types[type])
                if type == 'cursor':
                    columns = [field[0] for field in db_execute.description]
                    rows = db_execute.fetchall()
                    data = [dict(zip(columns, row)) for row in rows]
                    for d in data:
                        for key, value in d.items():
                            if isinstance(d[key], cx_Oracle.LOB):
                                d[key] = json.loads(str(value))
                    db_dto = {
                        "hasError": False,
                        "data": json.dumps(data, default=json_util.default)
                        #"data": json.dumps(data)
                    }
                else:
                    db_dto = {
                        "hasError": False,
                        "data": db_execute
                    }
            except Exception as e:
                raise Exception({'message': 'Ocurrio un error interno en OracleDB: ' + str(e), 'code': 'UPX603'})
            return db_dto
        elif (method == 'SP'):
            result = self.cursor.var(oracle_Types[type])
            params.append(result)
            return self.cursor.callproc(name, params)

    def close_execute(self):
        self.conn.close()
