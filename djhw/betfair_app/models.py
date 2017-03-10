from django.db import models
from django.utils import timezone

class BFChamp(models.Model):
    mcid = models.IntegerField(null=True)
    bfid=models.IntegerField()
    lid = models.IntegerField(null=True,db_index=True)
    sport = models.IntegerField(null=True)
    country_code = models.CharField(max_length=2,null=True)
    name = models.CharField(max_length=100,null=True)
    gender = models.IntegerField(null=True) # filled with a binding

class BFPlayer(models.Model):
    mpid = models.IntegerField(null=True)
    lid = models.IntegerField(null=True,db_index=True)
    name=models.CharField(max_length=100,db_index=True)
    gender = models.IntegerField(null=True) # filled with a binding

class BFEvent(models.Model):
    meid = models.IntegerField(null=True)
    bfid=models.IntegerField()
    lid = models.IntegerField(null=True,db_index=True)
    cid=models.ForeignKey(BFChamp,null=True,db_index=True)
    rid1 = models.IntegerField(null=True) # Runner id, for a future use
    rid2 = models.IntegerField(null=True)
    pid1=models.ForeignKey(BFPlayer, related_name='player1',null=True,db_index=True)
    pid2=models.ForeignKey(BFPlayer, related_name='player2',null=True,db_index=True)
    dt = models.DateTimeField(null=True,db_index=True)
    dtc = models.DateTimeField(null=True,db_index=True)
    dtip = models.DateTimeField(null=True)
    status = models.IntegerField(null=True) # 0 if ni, 1 if ip
    reversed = models.IntegerField(null=True)
    @property
    def dt_tz(self):
        return timezone.make_naive(self.dt)
    @property
    def dtc_tz(self):
        return timezone.make_naive(self.dtc)

class BFOdds(models.Model):
    eid=models.ForeignKey(BFEvent,db_index=True)
    b1odds = models.FloatField()
    b2odds = models.FloatField()
    b1size = models.FloatField(null=True)
    b2size = models.FloatField(null=True)
    l1odds = models.FloatField()
    l2odds = models.FloatField()
    l1size = models.FloatField(null=True)
    l2size = models.FloatField(null=True)
    dtc = models.DateTimeField(null=True,db_index=True)
    ip = models.NullBooleanField()
    @property
    def dtc_tz(self):
        return timezone.make_naive(self.dtc)
