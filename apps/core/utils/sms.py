import json

from services.utils import custom_request
from django.conf import settings


SMS_API_URL = settings.SMS_API_URL
SMS_API_TOKEN = settings.SMS_API_TOKEN

HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': SMS_API_TOKEN,
}


def api_send_sms(phone_number, text):
    """
        sends a text to the phone number
    """
    data = {
        'data': [
            {
                'phone_numbers': [str(phone_number)],
                'text': text,
            }
        ]
    }
    custom_request(url=f'{SMS_API_URL}/send-message/', data=json.dumps(data), headers=HEADERS)

