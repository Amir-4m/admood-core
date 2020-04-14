from django.db import models


class Device(models.Model):
    TYPE_PLATFORM = 1
    TYPE_OS = 2
    TYPE_VERSION = 3

    TYPE_CHOICES = (
        (TYPE_PLATFORM, "platform"),
        (TYPE_OS, "os"),
        (TYPE_VERSION, "version"),
    )

    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
    type = models.PositiveSmallIntegerField(choices=TYPE_CHOICES)
    title = models.CharField(max_length=20)

    def __str__(self):
        return f'{self.type} - {self.title}'


class PlatformManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type=Device.TYPE_PLATFORM)


class Platform(Device):
    objects = PlatformManager()

    def __init__(self, *args, **kwargs):
        self._meta.get_field('type').default = Device.TYPE_PLATFORM
        super().__init__(*args, **kwargs)

    class Meta:
        proxy = True


class OSManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type=Device.TYPE_OS)


class OS(Device):
    objects = OSManager()

    def __init__(self, *args, **kwargs):
        self._meta.get_field('type').default = Device.TYPE_OS
        super().__init__(*args, **kwargs)

    class Meta:
        proxy = True


class VersionManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type=Device.TYPE_VERSION)


class Version(Device):
    objects = VersionManager()

    def __init__(self, *args, **kwargs):
        self._meta.get_field('type').default = Device.TYPE_VERSION
        super().__init__(*args, **kwargs)

    class Meta:
        proxy = True
