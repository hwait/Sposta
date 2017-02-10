from django.db import models

class MChamp(models.Model):
    mcid = models.IntegerField(null=True,db_index=True)
    sport = models.IntegerField(null=True)
    countryid = models.IntegerField(null=True)
    name = models.CharField(max_length=100,null=True)
    prize = models.CharField(max_length=20,null=True)
    link = models.CharField(max_length=100,null=True)
    gender = models.IntegerField(null=True) # filled with a binding
    surface = models.IntegerField(null=True)

class MPlayer(models.Model):
    mpid = models.IntegerField(null=True,db_index=True)
    name=models.CharField(max_length=100,db_index=True)
    gender = models.IntegerField(null=True) # filled with a binding

class MEvent(models.Model):
    meid = models.IntegerField(null=True,db_index=True)
    champ=models.ForeignKey(MChamp,null=True,db_index=True)
    p1=models.ForeignKey(MPlayer, related_name='mplayer1',null=True,db_index=True)
    p2=models.ForeignKey(MPlayer, related_name='mplayer2',null=True,db_index=True)
    dt = models.DateTimeField(null=True,db_index=True)
