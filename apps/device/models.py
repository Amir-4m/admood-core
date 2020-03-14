from django.db import models


class Platform(models.Model):
    name = models.CharField(max_length=50)


class OS(models.Model):
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name = "OS"
        verbose_name_plural = "OS"


class OSVersion(models.Model):
    os = models.ForeignKey(OS, on_delete=models.CASCADE)
    version = models.CharField(max_length=10)

    class Meta:
        verbose_name = "OS Version"
        verbose_name_plural = "OS Versions"
