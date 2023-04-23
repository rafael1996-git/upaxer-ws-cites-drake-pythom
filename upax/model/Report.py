class Report:

    def __init__(self, name, questions):
        self.name = name
        self.questions = questions

    def build(self):
        result = {
            'reportName': self.name,
            'sections': self.questions
        }
        return result