PHOTO = 'photo'
VIDEO = 'video'
AUDIO = 'audio'
DOCUMENT = 'document'

FILE_TYPES = {
    PHOTO: ['.jpeg', '.jpg', '.png'],
    VIDEO: ['.mp4', '.gif', '.avi', '.wmv', '.mkv', '.flv', '.mov'],
    AUDIO: ['.mp3', '.wav', '.aac', '.ogg', '.wma'],
}


def file_type(extension):
    for k, v in FILE_TYPES.items():
        if extension in v:
            return k
    return DOCUMENT
