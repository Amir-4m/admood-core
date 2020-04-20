class Medium:
    WEB = 1
    IN_APP = 2
    TELEGRAM = 3
    INSTAGRAM = 4

    MEDIUM_CHOICES = (
        (WEB, "web"),
        (IN_APP, "in_app"),
        (TELEGRAM, "telegram"),
        (INSTAGRAM, "instagram"),
    )

    @classmethod
    def to_dict(cls):
        return [{'id': medium[0], 'title': medium[1]} for medium in cls.MEDIUM_CHOICES]


class MediumInterface:
    CHANNEL = 1
    POST = 2
    STORY = 3
    PUSH_NOTIFICATION = 4
    BANNER = 5
    NATIVE = 6

    MEDIUM_INTERFACE_CHOICES = (
        (CHANNEL, "channel"),
        (POST, "post"),
        (STORY, "story"),
        (PUSH_NOTIFICATION, "push_notification"),
        (BANNER, "banner"),
        (NATIVE, "native"),
    )


class MediumStatus:
    ACTIVE = 1
    SUSPEND = 2
    PAUSED = 3
    VERIFIED = 4

    MEDIUM_STATUS_CHOICES = (
        (ACTIVE, "active"),
        (SUSPEND, "suspend"),
        (PAUSED, "paused"),
        (VERIFIED, "verified"),
    )
