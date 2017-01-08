from django.db import models

class LSChamp(models.Model):
    sport = models.IntegerField()
    name = models.CharField(max_length=100)

class LSPlayer(models.Model):
    gender = models.IntegerField(null=True)
    name = models.CharField(max_length=50)
    link = models.CharField(max_length=100,null=True)

class LSEvent(models.Model):
    lsid=models.IntegerField(unique=True)
    cid=models.ForeignKey(LSChamp,null=True)
    pid1=models.ForeignKey(LSPlayer, related_name='player1',null=True)
    pid2=models.ForeignKey(LSPlayer, related_name='player2',null=True)
    dtc = models.DateTimeField(null=True)

class LSGame(models.Model):
    eid=models.ForeignKey(LSEvent,null=True)
    setn=models.IntegerField()
    sc1=models.IntegerField()
    sc2=models.IntegerField()
    prewin=models.IntegerField(null=True)
    dtc = models.DateTimeField(null=True)

class LSPoint(models.Model):
    gid=models.ForeignKey(LSGame,null=True)
    sc1=models.IntegerField()
    sc2=models.IntegerField()
    dtc = models.DateTimeField(null=True)
