from django.db import models

class Log(models.Model):
    name = models.CharField(max_length=100)
    dts = models.DateTimeField()
    counter = models.IntegerField(null=True)
    duration = models.IntegerField(null=True)
