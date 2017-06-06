from django.shortcuts import render
from django.views import View
from main_app.models import ALog
from livescores.models import LSChamp,LSEvent,LSPlayer, LSGame,LSPoint
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Max
from django.core import serializers
from django.http import JsonResponse
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
class LSInspect(View):
    def get(self, request):
        params=dict()
        template='ls_all.html'
        if request.method == 'GET':
            if 'cid' in request.GET:
                cid=int(request.GET['cid'])
                events=LSEvent.objects.select_related('pid1','pid2').filter(cid__id=cid)
                params['champ']=events[0].cid.name if len(events)>0 else ''
                params['events']=events
                template='ls_champ.html'
            if 'evid' in request.GET and 'isip' in request.GET:
                evid=int(request.GET['evid'])
                isip=request.GET['isip']=='1'
                event=LSEvent.objects.get(id=evid)
                params['event']=event
                #setsn=LSGame.objects.filter(eid=event).aggregate(Max('setn'))
                params['games']=[]
                games=LSGame.objects.filter(eid=event, setn__lt=6).order_by('dtc')
                for g in games:
                    points=LSPoint.objects.filter(gid=g).order_by('dtc')
                    params['games'].append([g,points])
                template='ls_event.html'
            else:
                params['cid']=''
                champs=LSChamp.objects.filter(lsevent__isnull=False).distinct()
                params['champs']=champs
        params['currentpage']='LS'
        return render(request,template,params)
    
class LSApiGet(View):
    def get(self, request):
        response_data = {}
        start=timezone.now()
        params=dict()
        try:
            dts=ALog.objects.filter(name='ls_get').latest('dts').dts
        except:
            dts=timezone.make_aware(datetime(2017, 1, 15))
        dte=dts+timedelta(hours=1)
        if(dte>start):
            response_data['result'] = 'None'
        else:
            champs=LSChamp.objects.filter(lid=None)
            players=LSPlayer.objects.filter(lid=None)
            LSEvent.objects.filter(cid=None).delete()
            events=LSEvent.objects.filter(lid=None)
            games=LSGame.objects.filter(dtc__gte=dts,dtc__lt=dte)
            points=LSPoint.objects.filter(gid__in=games)
            response_data['result'] = dte
            if len(players)>0:
                response_data['players'] = serializers.serialize('json', players)
            if len(champs)>0:
                response_data['champs'] = serializers.serialize('json', champs)
            if len(events)>0:
                response_data['events'] = serializers.serialize('json', events)
            if len(games)>0:
                response_data['games'] = serializers.serialize('json', games)
            if len(points)>0:
                response_data['points'] = serializers.serialize('json', points)
            #dtd=start-timedelta(days=7)
            #events=LSEvent.objects.filter(dtc__lt=dtd)
            #games=LSGame.objects.filter(eid__in=events)
            #LSPoint.objects.filter(gid__in=games).delete()
            #games.delete()
            #events.delete()
            log=ALog()
            log.name='ls_get'
            log.dts=dte
            log.counter=len(points)
            log.duration=(timezone.now()-start).total_seconds()
            log.save()
        return HttpResponse(JsonResponse(response_data), content_type="application/json")

class LSApiIds(View):
    def post(self, request):
        print request.body
        params=dict()
        pn=0
        en=0
        cn=0
        res=''
        if 'data' in request.POST:
            parts=request.POST['data'].split('-')
            for part in parts:
                t=part[:1]
                part=part.replace('c','').replace('p','').replace('e','')
                ps=part.split('.')
                for p in ps:
                    if p=='': 
                        continue
                    did,lid=map(int,p.split(':'))
                    if t=='c':
                        champ=LSChamp.objects.get(id=did)
                        champ.lid=lid
                        champ.save()
                    if t=='p':
                        player=LSPlayer.objects.get(id=did)
                        player.lid=lid
                        player.save()
                    if t=='e':
                        event=LSEvent.objects.get(id=did)
                        event.lid=lid
                        event.save()
                if t=='c':
                    cn=len(ps)
                if t=='p':
                    pn=len(ps)
                if t=='e':
                    en=len(ps)
        else:
            res='no data'
        res=self.clear_old(timezone.now()-timedelta(days=7))
        response_data = {}
        response_data['result'] = res
        response_data['players'] = pn
        response_data['champs'] = cn
        response_data['events'] = en
        return HttpResponse(JsonResponse(response_data), content_type="application/json")

    def clear_old(self,start):
        events=LSEvent.objects.filter(dtc__lt=start)
        evn=events.count()
        gn=0
        pn=0
        for ev in events:
            games=LSGame.objects.filter(eid=ev)
            gn+=games.count()
            for g in games:
                points=LSPoint.objects.filter(gid=g)
                pn+=points.count()
                points.delete()
            games.delete()
        events.delete()
        lschamps=LSChamp.objects.filter(lsevent__pk__isnull=True)
        lscn=lschamps.count()
        lschamps.delete()
        return 'CLEARED: %s champs, %s events, %s games and %s points' % (lscn, evn,gn,pn)
