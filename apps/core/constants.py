class Medium:
    WEB = "Web"
    IN_APP = "InAPP"
    TELEGRAM = "Telegram"
    INSTAGRAM = "Instagram"

    MEDIUM_CHOICES = (
        (WEB, "Web"),
        (IN_APP, "InAPP"),
        (TELEGRAM, "Telegram"),
        (INSTAGRAM, "Instagram"),
    )


class MediumInterface:
    CHANNEL = "Channel"
    POST = "Post"
    STORY = "Story"
    PUSH_NOTIF = "PushNotif"
    BANNER = "Banner"
    NATIVE = "Native"

    MEDIUM_INTERFACE_CHOICES = (
        (CHANNEL, "Channel"),
        (POST, "Post"),
        (STORY, "Story"),
        (PUSH_NOTIF, "PushNotif"),
        (BANNER, "Banner"),
        (NATIVE, "Native"),
    )


class MediumStatus:
    ACTIVE = "Active"
    SUSPEND = "Suspend"
    PAUSED = "PAUSED"
    VERIFIED = "VERIFIED"

    MEDIUM_STATUS_CHOICES = (
        (ACTIVE, "Active"),
        (SUSPEND, "Suspend"),
        (PAUSED, "PAUSED"),
        (VERIFIED, "VERIFIED"),
    )


class Bank:
    TEJARAT = "Tejarat"
    SAMAN = "Saman"

    BANK_CHOICES = (
        (TEJARAT, "Tejarat"),
        (SAMAN, "Saman"),
    )


class ServiceProvider:
    MTN = "MTN"
    IRANCELL = "Irancell"

    SERVICE_PROVIDER_CHOICES = (
        (MTN, "MTN"),
        (IRANCELL, "Irancell"),
    )


class Platform:
    PC = "PC"
    MOBILE = "Mobile"

    PLATFORM_CHOICES = (
        (PC, "PC"),
        (MOBILE, "Mobile")
    )
