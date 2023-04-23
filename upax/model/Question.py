class Question:

    def __init__(self, id_question, name, answer):
        self.id_question = id_question
        self.name = name
        self.answer = answer

    def build(self):
        result = {
            'id': self.id_question,
            'question': self.name,
            'answer': self.answer
        }
        return result