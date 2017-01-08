from django.db import models

class BFChamp(models.Model):
    bfid=models.IntegerField()
    lid = models.IntegerField(null=True)
    sport = models.IntegerField(null=True)
    country_code = models.CharField(max_length=2,null=True)
    name = models.CharField(max_length=100,null=True)
    gender = models.IntegerField(null=True) # filled with a binding

class BFPlayer(models.Model):
    lid = models.IntegerField(null=True)
    name=models.CharField(max_length=100)
    gender = models.IntegerField(null=True) # filled with a binding

class BFEvent(models.Model):
    bfid=models.IntegerField()
    lid = models.IntegerField(null=True)
    cid=models.ForeignKey(BFChamp,null=True)
    rid1 = models.IntegerField(null=True) # Runner id, for a future use
    rid2 = models.IntegerField(null=True)
    pid1=models.ForeignKey(BFPlayer, related_name='player1',null=True)
    pid2=models.ForeignKey(BFPlayer, related_name='player2',null=True)
    dt = models.DateTimeField(null=True)
    dtc = models.DateTimeField(null=True)
    dtip = models.DateTimeField(null=True)
    status = models.IntegerField(null=True) # 0 if ni, 1 if ip

class BFOdds(models.Model):
    eid=models.ForeignKey(BFEvent)
    b1odds = models.FloatField()
    b2odds = models.FloatField()
    b1size = models.FloatField(null=True)
    b2size = models.FloatField(null=True)
    l1odds = models.FloatField()
    l2odds = models.FloatField()
    l1size = models.FloatField(null=True)
    l2size = models.FloatField(null=True)
    dtc = models.DateTimeField(null=True)
    ip = models.NullBooleanField()
