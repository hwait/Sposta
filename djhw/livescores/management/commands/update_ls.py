from django.core.management.base import BaseCommand, CommandError
from livescores.models import LSChamp,LSPlayer,LSEvent,LSGame,LSPoint
from main_app.models import ALog
import datetime
from django.utils import timezone
import re
import requests
from django.conf import settings
import random
from livescores.logic import RepeatedTimer

class Command(BaseCommand):
    is_debug=True
    help = 'Refreshes livescores'
    counter=0
    gstart=timezone.now()
    timeout=7
    duration=3600

    def handle(self, *args, **options):
        self.timer = RepeatedTimer(self.timeout, self.reload, '')

    def reload(self, fake):
        start=timezone.now()
        rand=random.random()
        r=requests.get("http://www.livexscores.com/xml/tzmena.txt?%s" % rand)
        if(r.status_code == requests.codes.ok):
            #with open("ret0.txt", "w") as f:
            #    f.write(r.content)
            c=0
            retstr=''
            for ch in r.content:
                chc=ord(ch)
                retstr+=unichr(chc-c%2)
                c+=1
            #with open("ret%s.txt" % rand, "w") as f:
            #    f.write(retstr)
            allzmena=retstr.split('@')
            #self.stdout.write('%s\n'%(len(allzmena)), ending='')
            #allzmena0=map(int, allzmena[0].split(','))
            for i in range(1, len(allzmena)):
                zapas=allzmena[i].split('*')
                status=''
                cleared1=re.sub('<a[^>]+>','',zapas[2]).replace('</a>','')
                cleared1=re.sub('\([^)]+\)','',cleared1)
                cleared2=re.sub('<a[^>]+>','',zapas[3]).replace('</a>','')
                cleared2=re.sub('\([^)]+\)','',cleared2)
                if (self.is_debug):
                    self.stdout.write('%s - %s, zapas[2]=%s; zapas[3]=%s; \n'%(cleared1,cleared2,zapas[2],zapas[3]), ending='')
                if('/' in cleared1 and '/' in cleared2):
                    p1link=''
                    p2link=''
                    p1=cleared1
                    p2=cleared2
                else:
                    pattern=re.compile(r'<a class="player" href="([^"]+)" target="_blank">([^<]+)')
                    gr=pattern.search(zapas[2])
                    if gr==None:
                        p1link=''
                        p1=zapas[2]
                    else:
                        p1link=gr.group(1)
                        p1=gr.group(2)
                #if (self.is_debug):
                #    self.stdout.write('p1=%s,p1link=%s\n'%(p1,p1link), ending='')
                    gr=pattern.search(zapas[3])
                    if gr==None:
                        p2link=''
                        p2=zapas[3]
                    else:
                        p2link=gr.group(1)
                        p2=gr.group(2)
                #if (self.is_debug):
                #    self.stdout.write('p2=%s,p2link=%s\n'%(p2,p2link), ending='')
                points1=int(zapas[7].replace('15','1').replace('30','2').replace('40','3').replace('A','4'))
                points2=int(zapas[8].replace('15','1').replace('30','2').replace('40','3').replace('A','4'))
                serve=int(zapas[4])
                if ((((zapas[9]==6 and zapas[10]==6) or (zapas[11]==6 and zapas[12]==6) or (zapas[13]==6 and zapas[14]==6) or (zapas[15]==6 and zapas[16]==6) or (zapas[17]==6 and zapas[18]==6)) and serve < 3) or serve==5 or serve==6):
                    if (serve==5):
                        serve = 1
                    elif (serve==6):
                        serve = 2
                    if (self.is_debug):
                        self.stdout.write('points sum=%s\n'%(points1+points2), ending='')
                    if (points1 + points2==1 or points1 + points2==2 or points1 + points2==5 or points1 + points2==6 or points1 + points2==9 or points1 + points2==10 or points1 + points2==13 or points1 + points2==14 or points1 + points2==17 or points1 + points2==18 or points1 + points2==21 or points1 + points2==22 or points1 + points2==25 or points1 + points2==26 or points1 + points2==29 or points1 + points2==30 or points1 + points2==33 or points1 + points2==34 or points1 + points2==37 or points1 + points2==38 or points1 + points2==41 or points1 + points2==42 or points1 + points2==45 or points1 + points2==46 or points1 + points2==49 or points1 + points2==50 or points1 + points2==53 or points1 + points2==54 or points1 + points2==57 or points1 + points2==58 or points1 + points2==61 or points1 + points2==62 or points1 + points2==65 or points1 + points2==66 or points1 + points2==69 or points1 + points2==70 or points1 + points2==73 or points1 + points2==74):
                        if (serve==1):
                            serve = 2
                        elif (serve==2):
                            serve = 1
                #if (self.is_debug):
                #    self.stdout.write('serve=%s\n'%(serve), ending='')
                eid=int(zapas[0])
                champinfo=zapas[1] #1702/ATP Challenger - Happy Valley, Australia - Hard - Court 6
                p=champinfo.split(' - ')
                gender1=1 if 'atp' in p1link else 0
                gender2=1 if 'atp' in p2link else 0
                if p1link=='' and p2link!='':
                    gender1=gender2
                if p2link=='' and p1link!='':
                    gender2=gender1
                champname=p[0].split('/')[1] +', '+ p[1]
                if(zapas[20]=='Canc.'):
                    status='Canc.'
                    currentset=6
                else:
                    p=zapas[20].split()
                    if(len(p)>1):
                        if(p[1]==8):
                            status='Susp.'
                        elif(p[1]==9):
                            status='Postp.'
                        zapas[20]=p[0]
                    currentset=int(zapas[20])
                sets11,sets12=self.get_games(zapas[9]), self.get_games(zapas[10])
                sets21,sets22=self.get_games(zapas[11]),self.get_games(zapas[12])
                sets31,sets32=self.get_games(zapas[13]),self.get_games(zapas[14])
                sets41,sets42=self.get_games(zapas[15]),self.get_games(zapas[16])
                sets51,sets52=self.get_games(zapas[17]),self.get_games(zapas[18])
                self.stdout.write('zapas[5]=%s; zapas[6]=%s; \n'%(zapas[5],zapas[6]), ending='')
                p=zapas[6].split('-')
                if (len(p)<2):
                    lastgamewon=int(zapas[6])
                else:
                    lastgamewon=int(p[1])
                if currentset==0 or currentset==1:
                    gsc1=sets11
                    gsc2=sets12
                elif currentset==2:
                    gsc1=sets21
                    gsc2=sets22
                elif currentset==3:
                    gsc1=sets31
                    gsc2=sets32
                elif currentset==4:
                    gsc1=sets41
                    gsc2=sets42
                elif currentset==5:
                    gsc1=sets51
                    gsc2=sets52
                elif currentset==6:
                    gsc1=0
                    gsc2=0
                if (self.is_debug):
                    self.stdout.write('eid=%s,champ=%s, gender1=%s, gender2=%s\n'%(eid,champname,gender1,gender2), ending='')
                    self.stdout.write('%30s%5s%5s%5s%5s%5s|%5s\n'%(p1,sets11,sets21,sets31,sets41,sets51,points1), ending='')
                    self.stdout.write('%30s%5s%5s%5s%5s%5s|%5s\n'%(p2,sets12,sets22,sets32,sets42,sets52,points2), ending='')
                    self.stdout.write('currentset=%s, lastgamewon=%s\n'%(currentset,lastgamewon), ending='')
                end=timezone.now()
                event, created = LSEvent.objects.get_or_create(lsid=eid)
                if (created):
                    champ=self.save_champ(champname,2)
                    player1=self.save_player(p1,gender1,p1link)
                    player2=self.save_player(p2,gender2,p2link)
                    if (self.is_debug):
                        self.stdout.write('new event [%s] added %s - %s, cid=%s\n' % (event.id,player1.id,player2.id,champ.id), ending='')
                    event.cid=champ
                    event.pid1=player1
                    event.pid2=player2
                    event.dtc=end
                    event.save()
                game, created = LSGame.objects.get_or_create(eid=event,setn=currentset, sc1=gsc1, sc2=gsc2)
                if (created):
                    if (self.is_debug):
                        self.stdout.write('new game added %s\n' % game.id, ending='')
                    game.prewin=lastgamewon
                    game.dtc=end
                    game.serve=serve
                    game.save()
                    event.dtc=end
                    event.save()
                try:
                    point=LSPoint.objects.filter(gid=game).latest('dtc')
                    if (point.sc1!=points1 or point.sc2!=points2):
                        self.save_point(game,points1,points2,end, lastgamewon, event)
                except:
                    self.save_point(game,points1,points2,end, lastgamewon, event)
        end=timezone.now()
        log=ALog()
        log.name='update_ls'
        log.dts=start
        log.counter=self.counter
        log.duration=(end-start).total_seconds()
        log.save()
        if (self.is_debug):
            self.stdout.write('#%s (%s sec) executed for %s seconds\n' %(self.counter,self.duration-((end-self.gstart).total_seconds()+self.timeout),end-start), ending='')
        if (end-self.gstart).total_seconds()+self.timeout*3>=self.duration:
            self.timer.stop()
        self.counter+=1

    def save_point(self, game,sc1,sc2,dtc, lastgamewon, event):
        newpoint=LSPoint()
        newpoint.gid=game
        newpoint.sc1=sc1
        newpoint.sc2=sc2
        newpoint.dtc=dtc
        newpoint.save()
        game.prewin=lastgamewon
        game.dtc=dtc
        game.save()
        event.dtc=dtc
        event.save()


    def get_games(self, txt):
        p=txt.split('.')
        if len(p)>1:
            txt=p[0]
        return int(txt)

    def save_champ(self,name,sport):
        champ, created = LSChamp.objects.get_or_create(name=name, sport=sport)
        if (created):
            if (self.is_debug):
                self.stdout.write('created a new champ, id=%s\n' % (champ.id), ending='')
        return champ

    def save_player(self,name,gender,link):
        player, created = LSPlayer.objects.get_or_create(name=name)
        if (created):
            if (self.is_debug):
                self.stdout.write('created a new %s player %s, id=%s, link=%s\n' % (gender,name,player.id,link), ending='')
                player.gender=gender
                player.link=link
                player.save()
        return player
        