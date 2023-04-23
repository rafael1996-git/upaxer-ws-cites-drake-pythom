from upax.controller.LanguageController import LanguageController as tr
from queue import Queue
from threading import Thread


class Questionnaire:

    @staticmethod
    def structure(questionnaire):
        if questionnaire:
            questions = []
            for q in questionnaire['preguntas']:
                data = []
                answers = []
                if len(q['respuestas']) > 0:
                    data = data + q['respuestas']
                if len(q['alternas']) > 0:
                    data = data + q['alternas']
                for a in data:
                    answers.append({
                        'answerId': a['iddb'],
                        'answer': a['texto']
                    })
                questions.append({
                    'questionId': q['idbasedatos'],
                    'question': q['texto'],
                    'answers': answers
                })
            return {
                'questionnaireId': questionnaire['idencuesta'],
                'title': questionnaire['titulo'],
                'questions': questions
            }
        else:
            return None

    @staticmethod
    def translate_original(questionnaire, lang):
        if lang != 'es':
            questions_index = []
            text_list = []
            separator_list = []
            translate_text = ''
            counter = 0
            for q in questionnaire['questions']:
                text_list.append(q['question'])
                questions_index.append(counter)
                for a in q['answers']:
                    text_list.append(a['answer'])
                    counter += 1
                counter += 1
            for i, l in enumerate(text_list):
                translate_text += l + ' <; '
                if ((i if i > 0 else 1) % 50) == 0 or i >= (len(text_list) - 1):
                    separator_list.append(translate_text[:-3:])
                    translate_text = ''
            for s in separator_list:
                translate_text += tr().translate_text(lang, s)['TranslatedText'] + ' <;; '
            text_list = translate_text[:-4:].split('<;')
            for i, q in enumerate(questions_index):
                questionnaire['questions'][i]['question'] = text_list[q]
                for j, a in enumerate(questionnaire['questions'][i]['answers']):
                    a['answer'] = text_list[q + j + 1]
            questionnaire['title'] = tr().translate_text(lang, questionnaire['title'])['TranslatedText']
        questionnaire['lang'] = lang
        return questionnaire

    @staticmethod
    def translate_answered(answered, original, lang):
        for sa in answered:
            q = Queue()
            t = Thread(
                target=lambda a, arg1, arg2, arg3: a.put(Questionnaire.threads_translate_answered(arg1, arg2, arg3)),
                args=(q, sa, original, lang))
            t.start()
            t.join()
        return answered


    @staticmethod
    def threads_translate_answered(sa, original, lang):
        translated = list(filter(lambda x: x['questionId'] == sa['FIIDPREGUNTA'], original['questions']))[0]
        sa['FCTEXTOPREGUNTA'] = translated['question']
        answer = list(
            filter(lambda x: x['answerId'] == sa['FIIDPREGUNTAALTERNA'] or x['answerId'] == sa['FIIDOPCIONRESPUESTA'],
                   translated['answers']))
        answer = answer[0]['answer'] if answer else None
        if sa['FCTEXTORESPUESTACONTESTO']:
            sa['FCTEXTORESPUESTACONTESTO'] = sa['FCTEXTORESPUESTACONTESTO'] if sa['FIIDTIPOPREGUNTA'] == 23 or sa[
                'FIIDTIPOPREGUNTA'] == 26 else answer if answer else \
                tr().translate_text(lang, sa['FCTEXTORESPUESTACONTESTO'])['TranslatedText']
        return sa
