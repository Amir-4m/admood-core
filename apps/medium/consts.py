class Medium:
    WEB = "web"
    IN_APP = "in_app"
    TELEGRAM = "telegram"
    INSTAGRAM = "instagram"

    MEDIUM_CHOICES = (
        (WEB, "web"),
        (IN_APP, "in_app"),
        (TELEGRAM, "telegram"),
        (INSTAGRAM, "instagram"),
    )


class MediumInterface:
    CHANNEL = "channel"
    POST = "post"
    STORY = "story"
    PUSH_NOTIFICATION = "push_notification"
    BANNER = "banner"
    NATIVE = "native"

    MEDIUM_INTERFACE_CHOICES = (
        (CHANNEL, "channel"),
        (POST, "post"),
        (STORY, "story"),
        (PUSH_NOTIFICATION, "push_notification"),
        (BANNER, "banner"),
        (NATIVE, "native"),
    )


class MediumStatus:
    ACTIVE = "active"
    SUSPEND = "suspend"
    PAUSED = "paused"
    VERIFIED = "verified"

    MEDIUM_STATUS_CHOICES = (
        (ACTIVE, "active"),
        (SUSPEND, "suspend"),
        (PAUSED, "paused"),
        (VERIFIED, "verified"),
    )

