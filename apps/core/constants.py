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


class OS:
    WIN = "Win"
    LINUX = "Linux"
    OSX = "OSX"
    Android = "Android"
    IOS = "IOS"

    OS_CHOICES = (
        (WIN, "Win"),
        (LINUX, "Linux"),
        (OSX, "OSX"),
        (Android, "Android"),
        (IOS, "IOS"),
    )
