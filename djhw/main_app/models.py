from django.db import models

class ALog(models.Model):
    name = models.CharField(max_length=100)
    dts = models.DateTimeField()
    counter = models.IntegerField(null=True)
    duration = models.IntegerField(null=True)
