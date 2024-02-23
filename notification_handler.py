from twilio.rest import Client
import os
from dotenv import load_dotenv
load_dotenv(dotenv_path='.env')


TWILIO_SID=os.environ["TWILIO_ACCOUNT_SID"]
TWILIO_AUTH_TOKEN=os.environ["TWILIO_AUTH_TOKEN"]
TWILIO_VIRTUAL_NUMBER=os.getenv("TWILIO_PHONE_NUMBER")
MY_NUMBER=os.getenv("MY_NUMBER")
TWILIO_WHATSAPP_NUMBER=os.getenv("TWILIO_WHATSAPP_NUMBER")

class NotificationHandler:
    def __init__(self):
        self.client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

    def send_sms(self, message):
        try:
            message = self.client.messages \
                .create(
                from_= 'whatsapp:+14155238886',
                body=message,
                to='whatsapp:+447459555061'
            )

            print(f'\nWhatsApp notification sent successfully: {message.sid}')
        except Exception as e:
            print(f'Error sending message: {e}')