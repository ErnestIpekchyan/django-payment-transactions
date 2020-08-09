from django.db import models


class AutoDateMixin(models.Model):
    dt_created = models.DateTimeField('Дата создания', auto_now_add=True)
    dt_updated = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        abstract = True
