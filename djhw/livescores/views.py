from django.shortcuts import render
from django.views import View
from main_app.models import ALog
from livescores.models import LSChamp,LSEvent,LSPlayer, LSGame,LSPoint
from django.utils import timezone
import datetime
from django.db.models import Max

class Inspect(View):
    def get(self, request):
        params=dict()
        template='ls_all.html'
        
        if request.method == 'GET':
            if 'cid' in request.GET:
                cid=int(request.GET['cid'])
                events=LSEvent.objects.filter(cid__id=cid)
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
        return render(request,template,params)
