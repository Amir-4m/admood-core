import os


def file_type(name):
    image = 'image'
    video = 'video'
    audio = 'audio'
    document = 'document'

    file_types = {
        image: ['.jpeg', '.jpg', '.png'],
        video: ['.mp4', '.gif', '.avi', '.wmv', '.mkv', '.flv', '.mov'],
        audio: ['.mp3', '.wav', '.aac', '.ogg', '.wma'],
    }

    _, ext = os.path.splitext(name)

    for k, v in file_types.items():
        if ext in v:
            return k
    return document
