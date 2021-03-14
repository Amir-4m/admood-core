import os
import logging
import string
import random

import requests
from pid import PidFile


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

    _, ext = os.path.splitext(name.lower())

    for k, v in file_types.items():
        if ext in v:
            return k
    return document


def custom_request(url, method='post', **kwargs):
    try:
        logger.debug(f"[making request]-[method: {method}]-[URL: {url}]-[kwargs: {kwargs}]")
        req = requests.request(method, url, **kwargs)
        req.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.warning(
            f'[making request failed]-[response err: {e.response.text}]-[status code: {e.response.status_code}]'
            f'-[URL: {url}]-[exc: {e}]'
        )
        raise Exception(e.response.text)
    except requests.exceptions.ConnectTimeout as e:
        logger.critical(f'[request failed]-[URL: {url}]-[exc: {e}]')
        raise
    except Exception as e:
        logger.error(f'[request failed]-[URL: {url}]-[exc: {e}]')
        raise
    return req


class AutoFilter:
    """
    `admin.ModelAdmin` classes that has a filter field by `admin_auto_filters.filters.AutocompleteFilter`
     should extends from this class.
    """
    class Media:
        pass


def random_string(length):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def check_running(function_name):
    if not os.path.exists('./temps'):
        os.mkdir('./temps')
    file_lock = PidFile(str(function_name), piddir='./temps')
    try:
        file_lock.create()
        return file_lock
    except:
        return None


def stop_duplicate_task(func):
    def inner_function():
        file_lock = check_running(func.__name__)
        if not file_lock:
            logger.info(f">> [Another {func.__name__} is already running]")
            return False
        func()
        if file_lock:
            file_lock.close()
        return True
    return inner_function
