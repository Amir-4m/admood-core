class Medium:
    WEB = 1
    IN_APP = 2
    TELEGRAM = 3
    INSTAGRAM_POST = 4
    INSTAGRAM_STORY = 5
    PUSH_MOBILE = 6
    PUSH_WEB = 7

    MEDIUM_CHOICES = (
        (WEB, "web"),
        (IN_APP, "in_app"),
        (TELEGRAM, "telegram"),
        (INSTAGRAM_POST, "instagram_post"),
        (INSTAGRAM_STORY, "instagram_story"),
        (PUSH_MOBILE, "push_mobile"),
        (PUSH_WEB, "push_web"),
    )

    @classmethod
    def to_dict(cls):
        return [{'id': medium[0], 'title': medium[1]} for medium in cls.MEDIUM_CHOICES]
