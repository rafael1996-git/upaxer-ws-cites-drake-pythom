class SectionQuestion:

    def __init__(self, section, name, questions):
        self.section = section
        self.name = name
        self.questions = questions

    def build(self):
        response = {
            'name': self.name,
            'section': self.section,
            'questions': self.questions
        }
        return response