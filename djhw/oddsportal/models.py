from django.db import models

class OPChamp(models.Model):
    lid = models.IntegerField(null=True)
    sport = models.IntegerField()
    country = models.CharField(max_length=30)
    name = models.CharField(max_length=100,db_index=True)

class OPPlayer(models.Model):
    lid = models.IntegerField(null=True)
    name=models.CharField(max_length=50,db_index=True)
    gender = models.IntegerField()

class OPEvent(models.Model):
    lid = models.IntegerField(null=True)
    meid = models.IntegerField(null=True)
    reversed = models.IntegerField(null=True)
    champ = models.ForeignKey(OPChamp,null=True,db_index=True)
    p1=models.ForeignKey(OPPlayer, related_name='opplayer1',null=True,db_index=True)
    p2=models.ForeignKey(OPPlayer, related_name='opplayer2',null=True,db_index=True)
    sets1 = models.IntegerField(null=True)
    sets2 = models.IntegerField(null=True)
    dt = models.DateTimeField(null=True)
    dtc = models.DateTimeField(null=True)
    result = models.IntegerField(null=True)

class OPOdds(models.Model):
    ev = models.ForeignKey(OPEvent,null=True,db_index=True)
    w1 = models.FloatField(null=True,db_index=True)
    w2 = models.FloatField(null=True,db_index=True)
    w1max = models.FloatField(null=True,db_index=True)
    w2max = models.FloatField(null=True,db_index=True)
    dtc = models.DateTimeField(null=True)
    

