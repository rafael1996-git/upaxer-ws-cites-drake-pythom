import boto3


class LanguageController:

    def __init__(self):
        self.client = boto3.client('translate', 'us-east-1')

    def translate_text(self, language, text):
        try:
            t = self.client.translate_text(Text=text, SourceLanguageCode='es', TargetLanguageCode=language)
        except Exception as e:
            raise Exception({'message': 'Ocurrio un error con el servicio de Translate: ' + str(e), 'code': 'UPX605'})
        return t
        #response = self.client(
           # Text=text,
          #  SourceLanguageCode = 'auto',
         #   TargetLanguageCode = language
        #)
        #return response
