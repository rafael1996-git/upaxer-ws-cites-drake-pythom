import boto3
from botocore.exceptions import ClientError

AWS_REGION = "us-east-1"
SUBJECT = "NUEVA VISITA REGISTRADA CON ÉXITO - ADMINISTRADOR DE CITAS UPAXER"
CHARSET = "UTF-8"


class SendingEmail:

    def __init__(self):
        self.client = boto3.client('ses', AWS_REGION)

    def send_new_email(self, emailListToSend, folio, sender_email):

        for emailRecipient in emailListToSend:

            RECIPIENT = emailRecipient['FCDESCLARGA'] # FIITEMID = 80

            try:
                response = self.client.send_email(
                    Destination={
                        'ToAddresses': [
                            RECIPIENT,
                        ],
                    },
                    Message={
                        'Body': {
                            'Html': {
                                'Charset': CHARSET,
                                'Data': self.get_body(folio),
                            },
                        },
                        'Subject': {
                            'Charset': CHARSET,
                            'Data': SUBJECT,
                        },
                    },
                    Source=sender_email,
                )

            except ClientError as e:
                print(str(e))
            else:
                print("Mensaje enviado! ID Mensaje:"),
                print(response['MessageId'])

    @staticmethod
    def get_body(folio):
        return '<html><head></head><body><h1>Se ha registrado una nueva visita con el folio: <b> ' + folio + '</b>.</h1><p>Favor de revisarla en el Administrador de citas.</p><p>Atentamente<br>Administrador de citas <strong>UPAXER</strong></p></body></html>'