import requests
import json

from admood_core.settings import SMS_API_URL, SMS_API_TOKEN

SMS_API_URL = SMS_API_URL
SMS_API_TOKEN = SMS_API_TOKEN

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
    requests.post(f'{SMS_API_URL}/send-message/', data=json.dumps(data), headers=HEADERS)
