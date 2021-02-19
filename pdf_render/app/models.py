from django.db import models

from . import enums


class Document(models.Model):
    uploaded_dt = models.DateTimeField(auto_now_add=True)
    rendered_dt = models.DateTimeField(null=True)
    status = models.PositiveSmallIntegerField(
        choices=[(status.value, status.name) for status in enums.DocumentStatus],
        default=enums.DocumentStatus.PROCESSING,
    )
    n_pages = models.IntegerField(null=True)


class Image(models.Model):
    inserted_dt = models.DateTimeField(auto_now_add=True)
    page_num = models.IntegerField()
    image = models.ImageField(null=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
