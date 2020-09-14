from admood_core.settings import ADBOT_API_TOKEN, ADBOT_API_URL

JSON_HEADERS = {
    'Authorization': ADBOT_API_TOKEN,
    'Content-type': 'application/json'
}
HEADERS = {
    'Authorization': ADBOT_API_TOKEN,
}

CAMPAIGN_URL = f'{ADBOT_API_URL}/api/v1/campaigns/'
CONTENT_URL = f'{ADBOT_API_URL}/api/v1/contents/'
FILE_URL = f'{ADBOT_API_URL}/api/v1/files/'
