from django.core.management.base import BaseCommand, CommandError
from oddsportal.models import OPMeet
from main_app.models import ALog
import datetime
from django.utils import timezone
import re
import requests
from django.conf import settings

class Command(BaseCommand):
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
                name=m.group(3)
                if ('Doubles' in name or ' Mix' in name):
                    continue
                gender=1
                if('women' in name or 'WTA' in name):
                    gender=0
                link='http://www.oddsportal.com/tennis/%s/%s' % (country,linkname)
                if (settings.DEBUG):
                    self.stdout.write('********** %s (%s):\n' % (name,gender), ending='')
                r1=requests.get(link)
                if(r1.status_code == requests.codes.ok):
                    txt=re.sub(r'</?span[^>]*>', '', r1.content)
                    #with open("%s.html" % name, "w") as f:
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
                            if (settings.DEBUG):
                                self.stdout.write('[%s] %s - %s: %s (%s) - %s (%s) at %s, res=%s sets=%s:%s\ntrying to save... ' % (mid, p1, p2,w1, w1m, w2, w2m, dts, res, sets1, sets2), ending='')
                            meet, created = OPMeet.objects.get_or_create(sport=0,country=country,champ=name,player1=p1,player2=p2,gender=gender)
                            if (created):
                                if (settings.DEBUG):
                                    self.stdout.write('created a new record, id=%s\n' % (meet.id), ending='')
                            else:
                                if (settings.DEBUG):
                                    self.stdout.write('found #%s, ' % (meet.id))
                            if (meet.w1!=w1 or meet.w1max!=w1m or meet.w2!=w2 or meet.w2max!=w2m or meet.sets1!=sets1 or meet.sets2!=sets2):
                                if (settings.DEBUG):
                                    self.stdout.write('updated #%s, w1(%s->%s), w1m(%s->%s), w2(%s->%s), w2m(%s->%s)\n' % (meet.id,meet.w1,w1,meet.w1max,w1m,meet.w2,w2,meet.w2max,w2m), ending='')
                                meet.w1=w1
                                meet.w1max=w1m
                                meet.w2=w2
                                meet.w2max=w2m
                                meet.result=res
                                meet.sets1=sets1
                                meet.sets2=sets2
                                meet.dt=dts
                                meet.dtadd=timezone.now()
                                meet.save()
                            else:
                                if (settings.DEBUG):
                                    self.stdout.write('skipping (no difference)\n', ending='')
        end=timezone.now()
        log.dte=end
        log.duration=(end-start).total_seconds()
        log.save()
        if (settings.DEBUG):
            self.stdout.write('total execution is %s seconds\n' %(end-start), ending='')