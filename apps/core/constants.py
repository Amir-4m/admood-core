class MediumType:
    TELEGRAM = "Telegram"
    INSTAGRAM = "Instagram"
    PUSH_NOTIF = "PushNotif"
    BANNER = "Banner"
    NATIVE = "Native"

    MEDIUM_TYPE_CHOICES = (
        (TELEGRAM, "Telegram"),
        (INSTAGRAM, "Instagram"),
        (PUSH_NOTIF, "PushNotif"),
        (BANNER, "Banner"),
        (NATIVE, "Native"),
    )


class MediumInterface:
    WEB = "Web"
    IN_APP = "InAPP"
    CHANNEL = "Channel"
    POST = "Post"
    STORY = "Story"

    MEDIUM_INTERFACE_CHOICES = (
        (WEB, "Web"),
        (IN_APP, "InAPP"),
        (CHANNEL, "Channel"),
        (POST, "Post"),
        (STORY, "Story"),
    )


class Bank:
    TEJARAT = "Tejarat"
    SAMAN = "Saman"

    BANK_CHOICES = (
        (TEJARAT, "Tejarat"),
        (SAMAN, "Saman"),
    )