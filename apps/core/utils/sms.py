import json
import logging

from services.utils import custom_request
from admood_core.settings import SMS_API_URL, SMS_API_TOKEN

logger = logging.getLogger(__file__)

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
    custom_request(url=f'{SMS_API_URL}/send-message/', data=json.dumps(data), headers=HEADERS)

