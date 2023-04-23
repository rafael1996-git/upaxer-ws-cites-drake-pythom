from upax.db.DBPool import DBPool
from common.Constants import TYPE_FUNCTION, TYPE_RETURN_NUMBER, TYPE_RETURN_CURSOR
from upax.db.MongoPool import MongoPool
from upax.util.Log import message as log
import json


class VisitDAO():

    def __init__(self):
        self.client = DBPool()
        self.mongo = MongoPool()

    def insert_visit_contact(self, name, last_name, middle_name, phone_code, phone_number, cellphone, email, position):
        function_name = 'UPAXER.PAVISIT.FNINSERTCONTACT'
        payload = {
            'paName': name,
            'paLastName': last_name,
            'paMiddleName': middle_name,
            'paPosition': position,
            'paPhoneCode': phone_code,
            'paPhoneNumber': phone_number,
            'paCellphone': cellphone,
            'paMail': email,
            'paUsrModifico': 'UPAX_ADMIN'
        }
        result = self.client.execute(method=TYPE_FUNCTION, type=TYPE_RETURN_NUMBER, name=function_name, params=payload)
        return result

    def insert_company(self, bussines_name, comercial_name, nationality, rfc, activity):
        function_name = 'UPAXER.PAVISIT.FNINSERTCOMPANY'
        payload = {
            'paName': bussines_name,
            'paComercialName': comercial_name,
            'paNationality': nationality,
            'paRFC': rfc,
            'paActivity': activity,
            'paUsrModifico': 'UPAX_ADMIN'
        }
        result = self.client.execute(method=TYPE_FUNCTION, type=TYPE_RETURN_NUMBER, name=function_name, params=payload)
        return result

    def insert_company_address(self, type, country, state, locality, municipality, suburb, street, exterior_num,
                               interior_num, zip_code, phone_code, phone_number, lat, lon, comments):
        function_name = 'UPAXER.PACOMPANYADDRESS.FNINSERT'
        payload = {
            'paFCTYPE': type,
            'paFCCOUNTRY': country,
            'paFCSTATE': state,
            'paFCLOCALITY': locality,
            'paFCMUNICIPALITY': municipality,
            'paFCSUBURB': suburb,
            'paFCSTREET': street,
            'paFIEXTERIORNUM': exterior_num,
            'paFIINTERIORNUM': interior_num,
            'paFIZIPCODE': zip_code,
            'paFCPHONECODE': phone_code,
            'paFCPHONENUMBER': phone_number,
            'paFDLATITUDE': lat,
            'paFDLONGITUDE': lon,
            'paFCCOMMENTS': comments,
            'paUsrModifico': 'UPAX_ADMIN'
        }
        result = self.client.execute(method=TYPE_FUNCTION, type=TYPE_RETURN_NUMBER, name=function_name, params=payload)
        return result

    def company_has_address(self, id_company, id_company_address):
        function_name = 'UPAXER.PACOMPANYADDRESS.FNINSERTCOMPANYADDRESS'
        payload = {
            'paIdCompany': id_company,
            'paIdCompanyAddress': id_company_address,
            'paUsrModifico': 'UPAX_ADMIN'
        }
        result = self.client.execute(method=TYPE_FUNCTION, type=TYPE_RETURN_NUMBER, name=function_name, params=payload)
        return result

    def add_visit(self, register_type, priority, id_contact, id_company, folio, visit_date, user_who_modified):
        function_name = 'UPAXER.PAVISIT.FNINSERT'
        payload = {
            'pafiidregistertype': register_type,
            'pafiidpriority': priority,
            'pafiidcontact': id_contact,
            'pafiidcompany': id_company,
            'pafolio': folio,
            'pafechavisita': visit_date,
            'pausrmodifico': user_who_modified
        }
        result = self.client.execute(method=TYPE_FUNCTION, type=TYPE_RETURN_NUMBER, name=function_name, params=payload)
        return result

    def get_visit_info(self, folio):
        log("start: get_visit_info")
        function_name = 'UPAXER.PAVISIT.FNGETVISITINFO'
        payload = {
            'paFolio': folio
        }
        log("parameters: " + str(payload))
        result = self.client.execute(method=TYPE_FUNCTION, type=TYPE_RETURN_CURSOR, name=function_name, params=payload)
        log(result)
        return result

    def get_visit_survey(self, id_assign):
        function_name = 'UPAXER.PARESPCONTESTO.FNGETASSIGNSURVEY'
        payload = {
            'paIdAsignacion': id_assign
        }
        result = self.client.execute(method=TYPE_FUNCTION, type=TYPE_RETURN_CURSOR, name=function_name, params=payload)
        return result

    def get_survey_answers(self, answered_survey):
        answered_survey = answered_survey[0:len(answered_survey) - 1]
        answered_list = list(map(int, answered_survey.split(','))) if bool(answered_survey and answered_survey.strip()) else list()
        get_list = list()

        for i in answered_list:
            function_name = 'UPAXER.PARESPCONTESTO.FNGETANSWERS'
            payload = {
                'paEncuContestada': i
            }
            result = self.client.mul_execute(method=TYPE_FUNCTION, type=TYPE_RETURN_CURSOR, name=function_name, params=payload)
            get_list = get_list + json.loads(result['data'])
        self.client.close_execute()
        return get_list

    def insert_survey_translated(self, data):
        try:
            insert = self.mongo.insert_one('upaxer_answered_surveys', data)
            return insert
        except ValueError:
            return ValueError

    def getLastModifiedMongo(self, data, lang):
        try:
            list = []
            surveyList = []
            for item in data:
                if not item == '':
                    find = self.mongo.find('upaxer_answered_surveys', {'ANSWEREDSURVEYID': int(item), 'LANG': lang})
                    if len(find) > 0:
                        list.append(find)
            for i in list:
                modified = {}
                for j in i:
                    modified['ANSWEREDSURVEYID'] = j['ANSWEREDSURVEYID']
                    modified['LASTMODIFIED'] = j['LASTMODIFIED']
                surveyList.append(modified)
            return surveyList
        except ValueError:
            return ValueError

    def getLastModifiedOracle(self, data):
        function_name = 'UPAXER.PAVISIT.FNGETLASTANSWEREDSURVEY'
        list = []
        payload = {
            'ANSWEREDSURVEYSIDS': data
        }
        result = self.client.execute(method=TYPE_FUNCTION, type=TYPE_RETURN_CURSOR, name=function_name, params=payload)
        for i in json.loads(result['data']):
            list.append(i)
        return list

    def getSurveyDataMongo(self, data, lang):
        try:
            list = []
            for item in data:
                if not item == '':
                    find = self.mongo.find('upaxer_answered_surveys', {'ANSWEREDSURVEYID': int(item), 'LANG': lang})
                    if len(find) > 0:
                        for i in find:
                            list.append(i['DATA'])
            return list[0]
        except ValueError:
            return ValueError

    def deleteSurveyData(self, surveyId):
        listIds = surveyId.split(',')
        listIds = [int(i) for i in listIds]
        delete = self.mongo.delete_many('upaxer_answered_surveys', listIds, 'ANSWEREDSURVEYID')
        return delete

    def getSurveyData(self, surveyId):
        function_name = 'UPAXER.PAVISIT.FNGETSURVEYDATA'
        payload = {
            'SURVEYID': surveyId
        }
        result = self.client.execute(method=TYPE_FUNCTION, type=TYPE_RETURN_CURSOR, name=function_name, params=payload)
        jsonSurvey = json.loads(result['data'])[0]['FBJSON']
        return jsonSurvey

    def getQuestionnaire(self, questionnaireId):
        function_name = 'UPAXER.PAVISIT.FNGETQUESTIONNAIRE'
        payload = {
            'QUESTIONNAIREID': questionnaireId
        }
        result = self.client.execute(method=TYPE_FUNCTION, type=TYPE_RETURN_CURSOR, name=function_name, params=payload)
        return json.loads(result['data'])

    def getQuestionnaireInMongo(self, questionnaireId, lang):
        try:
            payload = {
                'questionnaireId': questionnaireId,
                'lang': lang
            }
            find = self.mongo.find('upaxer_answered_surveys', payload)
            return find
        except ValueError:
            return ValueError

    def insertQuestionnaireMongo(self, questionnaire):
        try:
            insert = self.mongo.insert_one('upaxer_answered_surveys', questionnaire)
            return insert
        except ValueError:
            return ValueError

    def validate_finished_status(self, folio):
        try:
            function_name = 'UPAXER.PAVISIT.FN_VALIDATE_FINISHED_STATUS'
            payload = {
                'FILE_VISIT': folio
            }
            result = self.client.execute(method=TYPE_FUNCTION, type=TYPE_RETURN_NUMBER, name=function_name,
                                         params=payload)
            return result['data']
        except ValueError:
            return ValueError

    def get_country_id(self, name):
        try:
            function = 'UPAXER.PAVISIT.FN_GET_COUNTRY_ID'
            parameters = {
                'COUNTRY_CODE': name
            }
            result = self.client.execute(method=TYPE_FUNCTION, type=TYPE_RETURN_NUMBER, name=function, params=parameters)
            if result['data'] > 0:
                return result['data']
            else:
                return 100
        except ValueError:
            return ValueError

    def get_email(self):
        function = 'UPAXER.PACATUNICO.FNOBTENERITEMID'
        parameters = {
            'paitemid':80
        }
        result = self.client.execute(method=TYPE_FUNCTION, type=TYPE_RETURN_CURSOR, name=function,
                                     params=parameters)
        return result['data']

    def get_sender_email(self):
        function = 'UPAXER.PAPARAMETRO.FNPARAMETRO'
        parameters = {
            'paParametro': 213
        }
        result = self.client.execute(method=TYPE_FUNCTION, type=TYPE_RETURN_CURSOR, name=function, params=parameters)
        return json.loads(result['data'])[0]['FCVALORPARAMETRO']