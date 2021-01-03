import os
import logging

import requests


logger = logging.getLogger(__name__)


def file_type(name):
    photo = 'photo'
    video = 'video'
    audio = 'audio'
    document = 'document'

    file_types = {
        photo: ['.jpeg', '.jpg', '.png'],
        video: ['.mp4', '.gif', '.avi', '.wmv', '.mkv', '.flv', '.mov'],
        audio: ['.mp3', '.wav', '.aac', '.ogg', '.wma'],
    }

    _, ext = os.path.splitext(name)

    for k, v in file_types.items():
        if ext in v:
            return k
    return document


def custom_request(url, method='post', **kwargs):
    try:
        req = requests.request(method, url, **kwargs)
        req.raise_for_status()
        return req
    
    except requests.exceptions.HTTPError as e:
        logger.critical(f'Request Failed. [{e.response.text}] - [{e.response.status_code}] - [{url}] - [{kwargs}]')
        raise Exception(e.response.text)
    except requests.exceptions.RequestException as e:
        logger.critical(f'Request Failed. [{e}] - [{url}] - [{kwargs}]')
        raise e
    except requests.exceptions.ConnectTimeout as e:
        logger.critical(f'Request Failed. [{e}] - [{url}] - [{kwargs}]')
        raise e

