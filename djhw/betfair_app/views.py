from django.shortcuts import render
from django.views import View
from main_app.models import ALog
from betfair_app.models import BFChamp,BFEvent,BFPlayer,BFOdds
from sposta_app.models import MChamp,MEvent
from django.utils import timezone
from django.utils.timezone import localtime
from datetime import datetime, timedelta
import plotly 
from plotly.offline.offline import _plot_html
from plotly.graph_objs import Scatter
from django.core import serializers
from django.http import JsonResponse
from django.http import HttpResponse

class BFInspect(View):
    def get(self, request):
        params=dict()
        template='bf_all.html'
        if request.method == 'GET':
            if 'cid' in request.GET:
                cid=int(request.GET['cid'])
                events=BFEvent.objects.select_related('pid1','pid2').filter(cid__id=cid)
                params['champ']=events[0].cid.name if len(events)>0 else ''
                params['events']=events
                template='bf_champ.html'
            if 'evid' in request.GET and 'isip' in request.GET:
                evid=int(request.GET['evid'])
                isip=request.GET['isip']=='1'
                event=BFEvent.objects.get(id=evid)
                params['event']=event
                oddschanges=BFOdds.objects.filter(eid=event,ip=isip).order_by('dtc')
                params['isip0']='' if isip else ' disabled'
                params['isip1']=' disabled' if isip else ''
                try:
                    goip=BFOdds.objects.filter(eid=event,ip=False).latest('dtc').dtc
                except:
                    goip=''
                params['goip']=goip
                params['oddschanges']=oddschanges
                plotly.tools.set_credentials_file(username='hwait', api_key='mYs3EJORl98E0vxkWvGr')
                xr=[i.dtc for i in oddschanges]
                y1r=[i.b1odds for i in oddschanges]
                y2r=[i.b2odds for i in oddschanges]
                figure_or_data = [Scatter(x=xr, y=y1r,mode = 'lines',name = event.pid1.name),Scatter(x=xr, y=y2r,mode = 'lines',name = event.pid2.name)]
                config = {}
                config['showLink'] = False
                plot_html = plot_html, plotdivid, width, height = _plot_html(
                    figure_or_data,config, True, '100%', 500, False)
                resize_script = ''
                if width == '100%' or height == '100%':
                    resize_script = (
                        ''
                        '<script type="text/javascript">'
                        'window.removeEventListener("resize");'
                        'window.addEventListener("resize", function(){{'
                        'Plotly.Plots.resize(document.getElementById("{id}"));}});'
                        '</script>'
                    ).format(id=plotdivid)
                params['graph'] = ''.join([
                            plot_html,
                            resize_script])
                template='bf_event.html'
            else:
                params['cid']=''
                champs=BFChamp.objects.filter(bfevent__isnull=False).distinct()
                params['champs']=champs
        return render(request,template,params)

class BFApiGet(View):
    def get(self, request):
        response_data = {}
        start=timezone.now()
        params=dict()
        try:
            dts=ALog.objects.filter(name='bf_get').latest('dts').dts
        except:
            dts=timezone.make_aware(datetime(2017, 1, 15))
        dte=dts+timedelta(hours=1)
        if(dte>start):
            response_data['result'] = 'None'
        else:
            champs=BFChamp.objects.filter(lid=None)
            players=BFPlayer.objects.filter(lid=None)
            events=BFEvent.objects.filter(lid=None)
            odds=BFOdds.objects.filter(dtc__gte=dts,dtc__lt=dte)
            response_data['result'] = dte
            if len(players)>0:
                response_data['players'] = serializers.serialize('json', players)
            if len(champs)>0:
                response_data['champs'] = serializers.serialize('json', champs)
            if len(events)>0:
                response_data['events'] = serializers.serialize('json', events)
            if len(odds)>0:
                response_data['odds'] = serializers.serialize('json', odds)
            #dtd=dts-timedelta(days=7)
            #events=BFEvent.objects.filter(dtc__lt=dtd)
            #BFOdds.objects.filter(eid__in=events).delete()
            #events.delete()
            log=ALog()
            log.name='bf_get'
            log.dts=dte
            log.counter=len(odds)
            log.duration=(timezone.now()-start).total_seconds()
            log.save()
        return HttpResponse(JsonResponse(response_data), content_type="application/json")

class BFApiInfo(View):
    def get(self, request):
        response_data = {}
        try:
            dts=ALog.objects.filter(name='bf_get').latest('dts').dts
        except:
            dts=timezone.make_aware(datetime(2017, 1, 15))
        champs=BFChamp.objects.filter(lid=None)
        players=BFPlayer.objects.filter(lid=None)
        events=BFEvent.objects.filter(lid=None)
        #dte=dts+timedelta(hours=1)
        #odds=BFOdds.objects.filter(dtc__gte=dts,dtc__lt=dte)
        response_data['result'] = dts
        if len(players)>0:
            response_data['players'] = serializers.serialize('json', players)
        if len(champs)>0:
            response_data['champs'] = serializers.serialize('json', champs)
        if len(events)>0:
            response_data['events'] = serializers.serialize('json', events)
        #if len(odds)>0:
        #    response_data['dts'] = serializers.serialize('json', odds)
        return HttpResponse(JsonResponse(response_data), content_type="application/json")

class BFApiIds(View):
    def post(self, request):
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
                        champ=BFChamp.objects.get(id=did)
                        champ.lid=lid
                        champ.save()
                    if t=='p':
                        player=BFPlayer.objects.get(id=did)
                        player.lid=lid
                        player.save()
                    if t=='e':
                        event=BFEvent.objects.get(id=did)
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
        events=BFEvent.objects.filter(dtc__lt=start)
        evn=events.count()
        oddn=0
        for ev in events:
            odds=BFOdds.objects.filter(eid=ev)
            oddn+=odds.count()
            odds.delete()
        events.delete()
        bfchamps=BFChamp.objects.filter(bfevent__pk__isnull=True)
        bfcn=bfchamps.count()
        bfchamps.delete()
        mevents=MEvent.objects.filter(dt__lt=start)
        mevn=mevents.count()
        mevents.delete()
        mchamps=MChamp.objects.filter(mevent__pk__isnull=True)
        mcn=mchamps.count()
        mchamps.delete()
        return 'CLEARED: %s champs, %s events, %s odds, %s mchamps, %s mevents' % (bfcn,evn,oddn, mcn, mevn)

