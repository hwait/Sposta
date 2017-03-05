from django.core.management.base import BaseCommand, CommandError
from oddsportal.models import OPChamp,OPEvent,OPPlayer, OPOdds
from main_app.models import ALog
import datetime
from django.utils import timezone
import re
import requests
from django.conf import settings

class Command(BaseCommand):
    is_debug=True
    help = 'Refreshes oddsportal data'

    def handle(self, *args, **options):
        start=timezone.now()
        log=ALog()
        log.name='update_op'
        log.dts=start
        log.save()
        ret=''
        r=requests.get("http://www.oddsportal.com/tennis/")
        #with open("op.html", "w") as f:
        #    f.write(r.content)
        if(r.status_code == requests.codes.ok):
            #'<a foo="f" href="/tennis/(^/+)/(^"+)">(^<+)</a>'
            for m in re.finditer(r'<a foo="f" href="/tennis/([^/]+)/([^"]+)">([^<]+)</a>', r.content):
                country=m.group(1)
                linkname=m.group(2)
                champname=m.group(3)
                #if ('Doubles' in champname or ' Mix' in champname):
                #    continue
                gender=1
                if('women' in champname or 'WTA' in champname):
                    gender=0
                link='http://www.oddsportal.com/tennis/%s/%s' % (country,linkname)
                if (self.is_debug):
                    self.stdout.write('********** %s (%s):\n' % (champname,gender), ending='')
                r1=requests.get(link)
                if(r1.status_code == requests.codes.ok):
                    txt=re.sub(r'</?span[^>]*>', '', r1.content)
                    #with open("%s.html" % champname, "w") as f:
                    #    f.write(txt)
                    gr=re.search(r'new PageTournament\(\{"id":"([^"]+)"', r1.content)
                    cid=gr.group(1)
                    linkm='http://www.oddsportal.com/ajax-sport-country-tournament/2/%s/X0/1' % cid
                    r2=requests.get(linkm)
                    if(r2.status_code == requests.codes.ok):
                        #with open("%s.json" % cid, "w") as f:
                        #    f.write(r2.content)
                        for m1 in re.finditer(r'xeid="([^"]+)"><td class="table-time datet t(\d+)-1-1-0-0 "></td><td class="name table-participant" colspan="\d"><a[^>]+>([^<]+)</a></td>(<td class="center bold table-odds table-score">([^<]+)</td>)?<td class="odds-nowrp">', txt):
                            mid=m1.group(1)
                            dts=timezone.make_aware(datetime.datetime.utcfromtimestamp(float(m1.group(2))))
                            p1,p2=m1.group(3).split(' - ')
                            sets1,sets2, res=0,0,0
                            if(m1.group(5)=='ret.'):
                                res=1
                            elif(m1.group(5)=='canc.'):
                                res=2
                            elif(m1.group(5)=='w.o.'):
                                res=3
                            elif(m1.group(5)=='award.'):
                                res=4
                            elif(m1.group(5)=='abn.'):
                                res=5
                            elif(m1.group(5)=='int.'):
                                res=6
                            elif (m1.group(5)!=None):
                                sets1,sets2=map(int, m1.group(5).split(':'))
                            ps=mid+'".\{"odds".\[\{"max".([^,]+),"avg".([^,]+),"res".[^,]+,"active".true,"oid"."[^"]+"\},\{"max".([^,]+),"avg".([^,]+),'
                            pattern=re.compile(ps)
                            gr1=pattern.search(r2.content)
                            if(gr1==None):
                                continue
                            w1m=float(gr1.group(1))
                            w1=float(gr1.group(2))
                            w2m=float(gr1.group(3))
                            w2=float(gr1.group(4))
                            if (self.is_debug):
                                self.stdout.write('[%s] %s - %s: %s (%s) - %s (%s) at %s, res=%s sets=%s:%s\ntrying to save... ' % (mid, p1, p2,w1, w1m, w2, w2m, dts, res, sets1, sets2), ending='')
                            champ=self.save_champ(champname,2,country)
                            player1=self.save_player(p1,gender)
                            player2=self.save_player(p2,gender)
                            meet, created = OPEvent.objects.get_or_create(champ=champ,p1=player1,p2=player2)
                            if (created):
                                if (self.is_debug):
                                    self.stdout.write('created a new record, id=%s\n' % (meet.id), ending='')
                            else:
                                if (self.is_debug):
                                    self.stdout.write('found #%s, ' % (meet.id))
                            if (meet.dt!=dts or meet.sets1!=sets1 or meet.sets2!=sets2 or meet.result!=res):
                                meet.dt=dts
                                meet.result=res
                                meet.sets1=sets1
                                meet.sets2=sets2
                                meet.dtc=timezone.now()
                                meet.save()
                            try:
                                odds=OPOdds.objects.filter(ev=meet).latest('dtc')
                                if (odds.w1!=w1 or odds.w1max!=w1m or odds.w2!=w2 or odds.w2max!=w2m):
                                    if (self.is_debug):
                                        self.stdout.write('updated #%s, w1(%s->%s), w1m(%s->%s), w2(%s->%s), w2m(%s->%s)\n' % (odds.id,odds.w1,w1,odds.w1max,w1m,odds.w2,w2,odds.w2max,w2m), ending='')
                                    self.save_odds(meet,w1,w1m,w2,w2m)
                            except:
                                self.save_odds(meet,w1,w1m,w2,w2m)
                                if (self.is_debug):
                                   self.stdout.write('new odds evid#[%s], w1(%s), w1m(%s), w2(%s), w2m(%s)\n' % (meet.id,w1,w1m,w2,w2m), ending='')
        end=timezone.now()
        log.dte=end
        log.duration=(end-start).total_seconds()
        log.save()
        if (self.is_debug):
            self.stdout.write('total execution is %s seconds\n' %(end-start), ending='')
        sys.exit()

    def save_champ(self,name,sport, country):
        champ, created = OPChamp.objects.get_or_create(name=name, sport=sport, country=country)
        if (created):
            if (self.is_debug):
                self.stdout.write('created a new champ, id=%s\n' % (champ.id), ending='')
        return champ

    def save_player(self,name,gender):
        player, created = OPPlayer.objects.get_or_create(name=name,gender=gender)
        if (created):
            if (self.is_debug):
                self.stdout.write('created a new %s player %s, id=%s, link=%s\n' % (gender,name,player.id), ending='')
        return player

    def save_odds(self,meet,w1,w1m,w2,w2m):
        odds=OPOdds()
        odds.ev=meet
        odds.w1=w1
        odds.w2=w2
        odds.w1max=w1m
        odds.w2max=w2m
        odds.dtc=timezone.now()
        odds.save()
        