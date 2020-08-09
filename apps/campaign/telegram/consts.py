from admood_core.settings import ADBOT_API_TOKEN

JSON_HEADERS = {
    'Authorization': ADBOT_API_TOKEN,
    'Content-type': 'application/json'
}
HEADERS = {
    'Authorization': ADBOT_API_TOKEN,
}

CAMPAIGN_URL = 'http://192.168.2.152:8000/api/v1/campaigns/'
CONTENT_URL = 'http://192.168.2.152:8000/api/v1/contents/'
FILE_URL = 'http://192.168.2.152:8000/api/v1/files/'
