from django.db import models

class OPMeet(models.Model):
    sport = models.IntegerField()
    country = models.CharField(max_length=30)
    champ = models.CharField(max_length=100)
    player1=models.CharField(max_length=50)
    player2=models.CharField(max_length=50)
    w1 = models.FloatField(null=True)
    w2 = models.FloatField(null=True)
    w1max = models.FloatField(null=True)
    w2max = models.FloatField(null=True)
    gender = models.IntegerField()
    sets1 = models.IntegerField(null=True)
    sets2 = models.IntegerField(null=True)
    dt = models.DateTimeField(null=True)
    dtadd = models.DateTimeField(null=True)
    result = models.IntegerField(null=True)

