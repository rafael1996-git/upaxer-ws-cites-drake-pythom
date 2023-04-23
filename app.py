from flask import Flask, request
import logging
import os
from datetime import datetime
from flask_cors import CORS, cross_origin
from common.Properties import path, path2
from upax.service.VisitService import VisitService
from upax.service.TokenService import TokenService
from upax.controller.LogController import res_s3


os.environ["NLS_LANG"] = "SPANISH_SPAIN.UTF8"
logger = logging.getLogger()
logger.setLevel(logging.INFO)
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
url_path = path


@app.route(url_path + '/add', methods=['POST'])
@cross_origin()
def add_visit():
    parameters = request.json
    path = request.path
    response = VisitService(parameters=parameters, path=path).add_visit()
    return response.body()


@app.route(url_path + '/get', methods=['POST'])
@cross_origin()
def get_visit():
    parameters = request.json
    path = request.path
    response = VisitService(parameters=parameters, path=path).get_task_detail()
    return response.body()


@app.route(path2 + '/create', methods=['POST'])
@cross_origin()
def create_user():
    parameters = request.json
    pathr = request.path
    response = TokenService(path=path, parameters=parameters).create_user()
    if response['hasError']:
        return {
            'code': 500,
            'message': response['response'],
            'path': pathr
        }, 500
    else:
        return response


@app.route(path2 + '/generate_token', methods=['POST'])
@cross_origin()
def get_token():
    parameters = request.json
    pathr = request.path
    print(request.path)
    print(request.json)
    response = TokenService(path=path, parameters=parameters).generate_token()
    print(str(response.__dict__))
    if response.status == 'UPX200':
        print('Estatdo exitoso')
        return {
            'code': response.status,
            'message': 'OK',
            'response': {
                'ExpiresIn': response.data['ExpiresIn'],
                'IdToken': response.data['IdToken'],
                'TokenType': response.data['TokenType']
            },
            'timestamp': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }
    else:
        print('Estatdo fallido')
        return {
            'code': response.status,
            'path': pathr,
            'message': response.detail,
            'timestamp': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }, 500


@app.errorhandler(500)
def not_found_error(error):
    print('Error en el servicio')
    print(str(error))
    data = {"errors": error.description}
    print(data)
    data = data['errors'] if 'errors' in data else data
    res_s3(data)
    return data, 500


if __name__ == '__main__':
    app.run()
