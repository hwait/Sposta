from django.shortcuts import render
from django.views import View
from main_app.models import ALog
from oddsportal.models import OPChamp,OPEvent,OPPlayer,OPOdds
from sposta_app.models import MChamp,MEvent,PlayerSetStats
from django.utils import timezone
from django.utils.timezone import localtime
from datetime import datetime, timedelta
import plotly 
from plotly.offline.offline import _plot_html
from plotly.graph_objs import Scatter
from django.core import serializers
from django.http import JsonResponse
from django.http import HttpResponse

class OPInspect(View):
    def get(self, request):
        params=dict()
        template='op_all.html'
        if request.method == 'GET':
            if 'cid' in request.GET:
                cid=int(request.GET['cid'])
                champ=OPChamp.objects.get(id=cid)
                events=OPEvent.objects.select_related('p1','p2').filter(champ__id=cid)
                params['champ']=champ
                params['events']=events
                template='op_champ.html'
            if 'evid' in request.GET:
                evid=int(request.GET['evid'])
                event=OPEvent.objects.select_related('p1','p2','champ').get(id=evid)
                params['event']=event
                oddschanges=OPOdds.objects.filter(ev=event).order_by('dtc')
                params['oddschanges']=oddschanges
                plotly.tools.set_credentials_file(username='hwait', api_key='mYs3EJORl98E0vxkWvGr')
                xr=[i.dtc for i in oddschanges]
                y1r=[i.w1 for i in oddschanges]
                y2r=[i.w2 for i in oddschanges]
                y1mr=[i.w1max for i in oddschanges]
                y2mr=[i.w2max for i in oddschanges]
                figure_or_data = [Scatter(x=xr, y=y1r,mode = 'lines',name = 'Avg '+event.p1.name),
                                  Scatter(x=xr, y=y2r,mode = 'lines',name = 'Avg '+event.p2.name),
                                  Scatter(x=xr, y=y1mr,mode = 'lines',name = 'Max '+event.p1.name),
                                  Scatter(x=xr, y=y2mr,mode = 'lines',name = 'Max '+event.p2.name),
                                  ]
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
                template='op_event.html'
            else:
                champs=OPChamp.objects.filter(opevent__isnull=False).distinct()
                params['champs']=champs
        return render(request,template,params)

class OPApiGet(View):
    def get(self, request):
        response_data = {}
        start=timezone.now()
        params=dict()
        try:
            dts=ALog.objects.filter(name='op_get').latest('dts').dts
        except:
            dts=timezone.make_aware(datetime(2017, 2, 10))
        dte=dts+timedelta(hours=1)
        if(dte>start):
            response_data['result'] = 'None'
        else:
            champs=OPChamp.objects.filter(lid=None)
            players=OPPlayer.objects.filter(lid=None)
            events=OPEvent.objects.filter(lid=None)
            odds=OPOdds.objects.filter(dtc__gte=dts,dtc__lt=dte)
            response_data['result'] = dte
            if len(players)>0:
                response_data['players'] = serializers.serialize('json', players)
            if len(champs)>0:
                response_data['champs'] = serializers.serialize('json', champs)
            if len(events)>0:
                response_data['events'] = serializers.serialize('json', events)
            if len(odds)>0:
                response_data['odds'] = serializers.serialize('json', odds)
            log=ALog()
            log.name='op_get'
            log.dts=dte
            log.counter=len(odds)
            log.duration=(timezone.now()-start).total_seconds()
            log.save()
        return HttpResponse(JsonResponse(response_data), content_type="application/json")

class OPApiIds(View):
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
                        champ=OPChamp.objects.get(id=did)
                        champ.lid=lid
                        champ.save()
                    if t=='p':
                        player=OPPlayer.objects.get(id=did)
                        player.lid=lid
                        player.save()
                    if t=='e':
                        event=OPEvent.objects.get(id=did)
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
        events=OPEvent.objects.filter(dtc__lt=start)
        evn=events.count()
        oddn=0
        for event in events:
            odds=OPOdds.objects.filter(ev=event)
            oddn+=odds.count()
            odds.delete()
        events.delete()
        opchamps=OPChamp.objects.filter(opevent__pk__isnull=True)
        opcn=opchamps.count()
        opchamps.delete()
        mevents=MEvent.objects.filter(dt__lt=start)
        mevn=mevents.count()
        for ev in mevents:
            PlayerSetStats.objects.filter(meid=ev.id).delete()
        mevents.delete()
        mchamps=MChamp.objects.filter(mevent__pk__isnull=True)
        mcn=mchamps.count()
        mchamps.delete()
        ret='CLEARED: %s champs, %s events, %s odds, %s mchamps, %s mevents' % (opcn,evn,oddn, mcn, mevn) if (bfcn+evn+oddn+mcn+mevn)>0 else 'CLEARED: none'
        return ret
