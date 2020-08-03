from django.db import models


class BaseModel(models.Model):
    pass

    class Meta:
        abstract = True


class File(models.Model):
    file = models.FileField()

    def __str__(self):
        return self.file.name
