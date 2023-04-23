from common.Utils import Utils as utils
from upax.dao.VisitDAO import VisitDAO
from upax.model.Response import Response
from upax.model.Error import Error
from upax.model.VisitInfo import VisitInfo
from upax.model.Reprogramming import Reprogramming
from upax.model.Report import Report
from common.Constants import SUCCESS_MESSAGE, SUCCESS_CODE, ERROR_CODE
import json
from upax.controller.LanguageController import LanguageController as tr
from upax.controller.SendingEmailController import SendingEmail as se
from flask import abort
import datetime
from threading import Thread
from queue import Queue
from upax.controller.LogController import req_s3
from upax.controller.Questionnaire import Questionnaire
from upax.util.Log import message as log


class VisitService:

    def __init__(self, path, parameters=None):
        self.path = path
        self.parameters = parameters
        req_s3(parameters)

    def add_visit(self):
        try:
            register_type = self.parameters['registerType']
            priority = self.parameters['priority']
            contact = self.parameters['contact']
            id_contact = self.insert_contact(data=contact)
            company = self.parameters['company']
            folio = self.parameters['folio']
            if 'visitDate' in self.parameters:
                visit_date = self.parameters['visitDate']
            else:
                visit_date = None
            user_who_modified = 'CITAS VISIT'
            if folio == None or folio == '':
                return Error(status=ERROR_CODE, id_service=None, source=self.path, title='Error in service',
                             detail='Missing folio data')

            id_company = self.insert_company(data=company)
            commercial_address = self.parameters['company']['address']['commercial']
            bussiness_address = self.parameters['company']['address']['fiscal']
            self.insert_address(id_company=id_company, address=commercial_address, type_address=1)
            self.insert_address(id_company=id_company, address=bussiness_address, type_address=2)
            response = VisitDAO().add_visit(register_type=register_type, priority=priority, id_contact=id_contact,
                                            id_company=id_company, folio=folio, visit_date=visit_date,
                                            user_who_modified=user_who_modified)
            if response['hasError']:
                abort(500, Error(status=ERROR_CODE, id_service=None, source=self.path, title='Error in service',
                                 detail='Folio data violated'))
            id_service = int(response['data'])
            if id_service:
                data = {
                    'folio': self.parameters['folio']
                }
                list_email = VisitDAO().get_email()
                sender_email = VisitDAO().get_sender_email()
                se().send_new_email(json.loads(list_email), self.parameters['folio'], sender_email)

                return Response(status=SUCCESS_CODE, data=data, message=SUCCESS_MESSAGE)
            else:
                abort(500, Error(status=ERROR_CODE, id_service=None, source=self.path, title='Error in service',
                                 detail='Folio repetido').create())
        except Exception as e:
            if len(e.args) > 0:
                if hasattr(e, 'args') and isinstance(e.args[0], dict):
                    if 'code' in e.args[0]:
                        abort(500, Error(status=e.args[0]['code'], id_service=None, source=self.path, title='Error in service', detail=e.args[0]['message']).create())
            else:
                abort(500, Error(status=e.description['code'], id_service=None, source=self.path, title='Error in service', detail=e.description['detail']).create())
            abort(500, Error(status=ERROR_CODE, id_service=None, source=self.path, title='Error in service',
                             detail='Ocurrio un error en el servicio: ' + str(e)).create())

    def get_task_detail(self):
        try:
            folio = self.parameters['folio']
            language = self.parameters['lang'].lower()
            log("request: " + str(self.parameters))
            VisitDAO().validate_finished_status(folio)
            visit_detail = VisitDAO().get_visit_info(folio=folio)
            data = {}
            visit_detail_data = json.loads(visit_detail['data'])
            for detail in visit_detail_data:
                data = VisitInfo(detail).build()
            reprogamming = list(
                filter(lambda x: (x['FIIDESTATUS'] == 4 or x['FIIDESTATUS'] == 9), json.loads(visit_detail['data'])))
            if data:
                data['location']['reprogramming'] = [Reprogramming(assign).build() for assign in reprogamming]
                id_assign = data['location']['visit']['id']
                visit_survey = VisitDAO().get_visit_survey(id_assign=id_assign)
                survey = json.loads(visit_survey['data'])
                if len(survey) > 0:
                    data['location']['visit']['initDate'] = int(datetime.datetime.timestamp(datetime.datetime.strptime(survey[0]['FECHA_INICIO'], "%d/%m/%Y %H:%M:%S") + datetime.timedelta(hours=5))) if survey[0]['FECHA_INICIO'] is not None else None if visit_survey else None
                    data['location']['visit']['endDate'] = int(datetime.datetime.timestamp(datetime.datetime.strptime(survey[0]['FECHA_FIN'], "%d/%m/%Y %H:%M:%S") + datetime.timedelta(hours=5))) if survey[0]['FECHA_FIN'] is not None else None if visit_survey else None
                aux = json.loads(visit_survey['data'])
                if len(aux) > 0:
                    report = self.set_report_info(json.loads(visit_survey['data']), language)
                else:
                    report = ()
                data['report'] = report
            return Response(status=SUCCESS_CODE, message=SUCCESS_MESSAGE, data=data)
        except Exception as e:
            id_service = self.parameters['folio']
            if hasattr(e, 'args') and isinstance(e.args[0], dict):
                if 'code' in e.args[0]:
                    abort(500, Error(status=e.args[0]['code'], id_service=id_service, source=self.path, title='Error in service', detail=e.args[0]['message']).create())
            abort(500, Error(status=ERROR_CODE, id_service=id_service, source=self.path, title='Error in service', detail='Ocurrio un error en el servicio: ' + str(e)).create())

    def insert_contact(self, data):
        name = data['name']
        last_name = data['pLastName']
        middle_name = data['mLastName']
        phone_code = data['phoneCode']
        phone_number = data['phoneNumber']
        cellphone = data['cellphone']
        email = data['email']
        position = data['position']
        response = VisitDAO().insert_visit_contact(name=name, last_name=last_name, middle_name=middle_name,
                                                   phone_code=phone_code, phone_number=phone_number,
                                                   cellphone=cellphone,
                                                   email=email, position=position)
        return int(response['data'])

    def insert_company(self, data):
        bussines_name = data['bussinesName']
        comercial_name = data['commercialName']
        nationality = '1'
        rfc = data['rfc']
        activity = data['activity']
        response = VisitDAO().insert_company(bussines_name=bussines_name, comercial_name=comercial_name,
                                             nationality=nationality, rfc=rfc, activity=activity)
        return int(response['data'])

    def insert_address(self, id_company, address, type_address):
        country = VisitDAO().get_country_id(address['country'])
        state = address['state']
        locality = address['locality']
        municipality = address['municipality']
        suburb = address['suburb']
        street = address['street']
        exterior_num = address['exteriorNum']
        interior_num = address['interiorNum']
        zip_code = address['zipCode']
        phone_code = address['phoneCode']
        phone_number = address['phoneNumber']
        lat = 0
        '''address['lat']'''
        lon = 0
        '''address['lon']'''
        comments = '' '''address['comments']'''
        type = type_address
        company_address = VisitDAO().insert_company_address(type=type, country=country, state=state,
                                                            locality=locality, municipality=municipality,
                                                            suburb=suburb,
                                                            street=street, exterior_num=exterior_num,
                                                            interior_num=interior_num,
                                                            zip_code=zip_code, phone_code=phone_code,
                                                            phone_number=phone_number,
                                                            lat=lat, lon=lon, comments=comments)
        id_company_address = int(company_address['data'])
        response = VisitDAO().company_has_address(id_company=id_company, id_company_address=id_company_address)
        return int(response['data'])

    def set_report_info(self, data, lang):
        result = list()
        survey_group = utils.group_by_param(field_name='FIIDENCUESTA', list_data=data)
        questionnaireId = data[0]['FIIDENCUESTA']
        getQuestionnaire = self.getQuestionnaire(questionnaireId)[0]
        #obtiene la version y el questionario de oracle
        if getQuestionnaire:
            version = getQuestionnaire['VERSION']
            questionnaire = getQuestionnaire['QUESTIONNAIRE']
        else:
            version = None
            questionnaire = None
        #MONGO---------------------------------------
        getInMongo = self.getQuestionnaireInMongo(questionnaireId, lang)
        if not len(getInMongo) > 0:
            questionnaire_structure = Questionnaire.structure(questionnaire)
            questionnaire_structure['version'] = version
            questionnaire_translate = Questionnaire.translate_original(questionnaire_structure, lang)
            insert = VisitDAO().insertQuestionnaireMongo(questionnaire_translate)
            questionnaireLang = questionnaire_translate if insert else None
            #questionnaireLang = self.translate_questionnaire(questionnaire, lang, version)
        else:
            #flujo normal
            questionnaireLang = getInMongo[0]
        for key, value in survey_group.items():
            #solo agrega un titulo
            report_name = getInMongo[0]['title'] if len(getInMongo) > 0 else value[0]['FCNOMBRETAREA']
            #lista vacia
            answered_survey_list = list()
            #'FIIDENCUCONTESTADA': 1410983,
            answered_survey = ''
            for resp in value:
                if not resp['FIIDENCUCONTESTADA'] == None:
                    answered_survey += (str(resp['FIIDENCUCONTESTADA']) + ',')
            survey_list = answered_survey.split(',')
            # 'FIIDENCUCONTESTADA': 1410983,
            for i in range(0, len(survey_list), 100):
                surveys = ','.join(survey for survey in survey_list[i: i + 100])
                answered_survey_list.append(surveys)
            question_data = list()
            for surveys in answered_survey_list:
                #AQUI------------------ obtiene las respuestas
                survey_answers = VisitDAO().get_survey_answers(answered_survey=surveys)
                #survey_answers_validate = utils.merge_answers_template(survey_answers, getInMongo)
                getSurveyData = survey_answers if lang == 'es' else Questionnaire.translate_answered(survey_answers, questionnaireLang, lang)
                #getSurveyData = self.questionnaireTranslate(survey_answers, questionnaireLang, lang) if questionnaireLang else None
                if getSurveyData:
                    question_data.extend(getSurveyData)
            #AQUI------------------
            section_item = utils.get_section(question_data)
            #AQUI------------------
            question_response = list()
            for item in section_item:
                question_response.append(item)
            result.append(Report(name=report_name, questions=question_response).build())
        return result

    def insert_survey_translated(self, surveyId, lastModified, lang, data):
        list = json.loads(data)

        for item in list:
            item['FCTEXTOPREGUNTA'] = (tr().translate_text(lang, item['FCTEXTOPREGUNTA']))['TranslatedText']
            item['FCTEXTORESPUESTACONTESTO'] = (tr().translate_text(lang, item['FCTEXTORESPUESTACONTESTO']))[
                'TranslatedText'] if item['FCTEXTORESPUESTACONTESTO'] is not None else None
        insertDataEs = {
            'ANSWEREDSURVEYID': int(surveyId),
            'LASTMODIFIED': lastModified,
            'LANG': 'es',
            'DATA': data
        }
        insertEs = VisitDAO().insert_survey_translated(insertDataEs)

        insertDataEn = {
            'ANSWEREDSURVEYID': int(surveyId),
            'LASTMODIFIED': lastModified,
            'LANG': lang,
            'DATA': json.dumps(list)
        }
        insertEn = VisitDAO().insert_survey_translated(insertDataEn)
        if insertEs is not None and insertEn is not None:
            return json.dumps(list)
        else:
            return 'Error'

    def updateSurveyDataMongo(self, surveyId, lastModified, lang, data):
        delete = VisitDAO().deleteSurveyData(surveyId)
        if delete['n'] > 0:
            return self.insert_survey_translated(surveyId, lastModified, lang, data)
        else:
            return 'Error'

    def getQuestionnaire(self, questionnaireId):
        return VisitDAO().getQuestionnaire(questionnaireId)

    def getQuestionnaireInMongo(self, questionnaireId, lang):
        return VisitDAO().getQuestionnaireInMongo(questionnaireId, lang)

    def translate_questionnaire(self, questionnaire, lang, version):
        structure = {}
        questions = []
        if questionnaire:
            for item in questionnaire['preguntas']:
                q = Queue()
                t = Thread(target=lambda a, arg1, arg2: a.put(self.thread_translate_questionnaire(arg1, arg2)),
                           args=(q, item, lang))
                t.start()
                t.join()
                questions.append(q.get())
            aux = ''
            counter = 0
            list_counter = []
            for q in questions:
                ansq = []
                for a in q['answers']:
                    aux = aux + a['answer'] + '; '
                    ansq.append(counter)
                    counter = counter + 1
                aux = aux + q['question'] + '; '
                list_counter.append({'index': counter, 'ansq': ansq})
                counter = counter + 1
            new_list = questions.copy()
            aux = aux.split(';')
            aux6 = []
            aux8 = ''
            counter2 = 0
            for y, a in enumerate(aux):
                if counter2 > 5 or y > len(aux):
                    aux8 = aux8 + a + ' ; '
                    aux6.append(aux8)
                    counter2 = 0
                    aux8 = ''
                aux8 = aux8 + a + ' ; '
                counter2 = counter2 + 1
            '''for i, n in enumerate(new_list):
                n['question'] = aux[i]
                if list_counter[i]['ansq']:
                    for asd in n['answers']:'''
            aux9 = []
            for test1 in aux6:
                aux9.append(tr().translate_text(lang, test1)['TranslatedText'])
            translate10 = ''
            for aux10 in aux9:
                translate10 = translate10 + aux10
            aux2 = translate10.split(';')
            for i, auxt in enumerate(list_counter):
                new_list[i]['question'] = aux[auxt['index']]
                for j, d in enumerate(new_list[i]['answers']):
                    d['answer'] = aux[auxt['ansq'][j]]


            structure['title'] = tr().translate_text(lang, questionnaire['titulo'])['TranslatedText']
            structure['questions'] = questions
            structure['questionnaireId'] = questionnaire['idencuesta']
            structure['version'] = version
            structure['lang'] = lang
            insert = VisitDAO().insertQuestionnaireMongo(structure)
            if insert is not None:
                return structure
            else:
                return None
        else:
            return None

    @staticmethod
    def thread_translate_questionnaire(item, lang):
        answers = []
        data = []
        translate = ''
        if len(item['respuestas']) > 0:
            data = data + item['respuestas']
        if len(item['alternas']) > 0:
            data = data + item['alternas']
        for sub_item in data:
            answers.append({
                'answerId': sub_item['iddb'],
                'answer': sub_item['texto']
            })
            translate = translate + sub_item['texto'] + '; '
        translate = translate + item['texto']
        #list_tra = tr().translate_text(lang, translate)['TranslatedText'].split(';') if translate else ''
        list_tra = translate.split(';')
        for index, i in enumerate(list_tra):
            if index < (len(answers)):
                answers[index]['answer'] = i
        return {
            'questionId': item['idbasedatos'],
            'question': list_tra[-1],
            'answers': answers
        }


    def translateQuestionnaire(self, questionnaire, lang, version):
        structure = {}
        questions = []
        if questionnaire:
            for item in questionnaire['preguntas']:
                q = Queue()
                t = Thread(target=lambda a, arg1, arg2: a.put(self.thread_questionnaire(arg1, arg2)), args=(q, item, lang))
                t.start()
                t.join()
                questions.append(q.get())
            structure['title'] = questionnaire['titulo'] if lang == 'es' else (tr().translate_text(lang, questionnaire['titulo']))['TranslatedText']
            structure['questions'] = questions
            structure['questionnaireId'] = questionnaire['idencuesta']
            structure['version'] = version
            structure['lang'] = lang
            insert = VisitDAO().insertQuestionnaireMongo(structure)
            if insert is not None:
                return structure
            else:
                return None
        else:
            return None

    @staticmethod
    def thread_questionnaire(item, lang):
        answers = []
        data = []

        if len(item['respuestas']) > 0:
            data = data + item['respuestas']
        if len(item['alternas']) > 0:
            data = data + item['alternas']

        for subItem in data:
            q = Queue()
            t = Thread(target=lambda a, arg1, arg2: a.put(VisitService.translate(arg1, arg2)), args=(q, subItem, lang))
            t.start()
            t.join()
            answers.append(q.get())

        question = {
            'questionId': item['idbasedatos'],
            'question': item['texto'] if lang == 'es' else (tr().translate_text(lang, item['texto']))[
                'TranslatedText'],
            'answers': answers
        }
        return question

    @staticmethod
    def translate(subItem, lang):
        return {
            'answerId': subItem['iddb'],
            'answer': subItem['texto'] if lang == 'es' else (tr().translate_text(lang, subItem['texto']))[
                'TranslatedText']
        }

    @staticmethod
    def questionnaireTranslate(original, translated, lang):
        for item in original:
            q = Queue()
            t = Thread(target=lambda a, arg1, arg2, arg3: a.put(VisitService.thread_translate(arg1, arg2, arg3)), args=(q, item, translated, lang))
            t.start()
            t.join()
        return json.dumps(original)

    @staticmethod
    def thread_translate(item, translated, lang):
        answers = list(filter(lambda x: x['questionId'] == item['FIIDPREGUNTA'], translated['questions']))
        if answers:
            answers = answers[0]['answers']
        answer_list = list(filter(lambda x: x['answerId'] == item['FIIDPREGUNTAALTERNA'] or x['answerId'] == item['FIIDOPCIONRESPUESTA'], answers))
        answer = answer_list[0]['answer'] if len(answer_list) > 0 else None
        item['FCTEXTOPREGUNTA'] = list(filter(lambda x: x['questionId'] == item['FIIDPREGUNTA'], translated['questions']))
        if item['FCTEXTOPREGUNTA']:
            item['FCTEXTOPREGUNTA'] = item['FCTEXTOPREGUNTA'][0]['question']
        item['FCTEXTORESPUESTACONTESTO'] = item['FCTEXTORESPUESTACONTESTO'] if lang == 'es' else answer if answer is not None else ((tr().translate_text(lang, item['FCTEXTORESPUESTACONTESTO']))['TranslatedText'] if item['FCTEXTORESPUESTACONTESTO'] is not None else None)
        return item
