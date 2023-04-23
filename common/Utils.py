from upax.model.Question import Question
from operator import itemgetter
import itertools


class Utils:

    @staticmethod
    def get_priority(str):
        payload = {
            'ALTA': 1,
            'MEDIA': 2,
            'BAJA': 3
        }
        return payload[str]

    @staticmethod
    def get_register_type(str):
        payload = {
            'STANDARD': 1,
            'ADVANCED': 2
        }
        return payload[str]

    @staticmethod
    def set_visit_status(status):
        payload = {
            0: 'Pendiente',
            1: 'En revisión',
            2: 'En proceso',
            3: 'Rechazada',
            4: 'Finalizada'
        }
        return payload[status]

    @staticmethod
    def set_status(id_status):
        payload = {
            0: 'Eliminada',
            1: 'Libre',
            2: 'Sin Terminar',
            3: 'Terminada',
            4: 'Cancelada por Usuario',
            5: 'Abandonada',
            6: 'Vencida',
            7: 'Evidencia extraida por usuario',
            8: 'Desactivada',
            9: 'Replantada',
            12: 'Sincronizando Multimedia'
        }
        result = payload[id_status] if id_status in payload else 'Desactivada'
        return result

    @staticmethod
    def group_by_param(field_name, list_data):
        response = {}
        for key, group in itertools.groupby(sorted(list_data, key=itemgetter(field_name)), key=lambda x: x[field_name]):
            response[key] = list(group)
        return response

    @staticmethod
    def get_section(list_data):
        sections = []
        count = 0
        for data in list_data:
            if (data['FIIDTIPOPREGUNTA'] == 12):
                name = '' if isinstance(data['FCTEXTOPREGUNTA'], list) and len(data['FCTEXTOPREGUNTA']) == 0 else data[
                    'FCTEXTOPREGUNTA']
                count += 1
                sections.append({
                    'name': name,
                    'questions': [],
                    'id': count
                })
            else:
                question_id = data['FIIDPREGUNTA']
                question = '' if isinstance(data['FCTEXTOPREGUNTA'], list) and len(data['FCTEXTOPREGUNTA']) == 0 else \
                data['FCTEXTOPREGUNTA']
                answer = data['FCTEXTORESPUESTACONTESTO']
                if answer is not None:
                    sections[count - 1]['questions'].append(
                        Question(id_question=question_id, name=question, answer=answer).build())
                else:
                    if not (data['FIIDTIPOPREGUNTA'] == 17 or data['FIIDTIPOPREGUNTA'] == 27):
                        sections[count - 1]['questions'].append(Question(id_question=question_id, name=question, answer="Sin respuesta").build())
        return sections

    # las preguntas tienen que estar ordenadas
    @staticmethod
    def merge_answers_template(answers, template):

        merge_answers_template = []
        template_answers = template[0]["questions"]
        tamaño_template_answers = len(template_answers)
        first_answers_id = answers[0]["FIIDPREGUNTA"]
        # first_template_answers_id = template_answers[0]["questionId"]
        while first_answers_id != template_answers[0]["questionId"]:
            template_answers.pop(0)
        # recorrer las preguntas del template para de aqui armarlo
        # no pueden existir mas respuestas que preguntas
        '''
        for i in range(len(template_answers)):
            if template_answers[i]["questionId"] == answers[i]["FIIDPREGUNTA"]:
                print("iguales")
                merge_answers_template.append(answers[i])
            else:
                print("no son iguales")
                merge_answers_template.append(default_answer(template_answers[i]["questionId"],
                                                             template_answers[i]["question"],
                                                             "Sin respuesta"))'''
        x = 0
        y = 0
        while x < len(template_answers):
            if y < len(answers) and template_answers[x]["questionId"] == answers[y]["FIIDPREGUNTA"]:
                print("iguales")
                merge_answers_template.append(answers[y])
                x = x + 1
                y = y + 1
            else:
                print("no son iguales")
                pregunta_default = default_answer(template_answers[x]["questionId"],
                                                             template_answers[x]["question"],
                                                             "Sin respuesta")
                merge_answers_template.append(pregunta_default)
                x = x + 1
        return merge_answers_template

def default_answer(questionId, textoPregunta, textoRespuesta):
    answer = {
        'FIIDENCUCONTESTADA': '',
        'FIORDEN': '',
        'FIIDPREGUNTA': questionId,  # IMPORTANTE
        'FCTEXTOPREGUNTA': textoPregunta,  # data['FCTEXTOPREGUNTA']
        'FCTEXTORESPUESTACONTESTO': textoRespuesta,  # FCTEXTORESPUESTACONTESTO
        'FIIDTIPOPREGUNTA': '',
        'FIIDOPCIONRESPUESTA': '',
        'FIIDPREGUNTAALTERNA': ''
    }
    return answer
