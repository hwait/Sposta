from django.shortcuts import render
from django.views import View
from main_app.models import ALog
from sposta_app.models import MChamp, MPlayer,MEvent
from betfair_app.models import BFChamp,BFEvent,BFPlayer,BFOdds
from livescores.models import LSChamp,LSEvent,LSPlayer,LSGame,LSPoint
from django.utils import timezone
from datetime import datetime
from django.db.models import Max
from betfair_app.models import BFEvent
from livescores.models import LSEvent
import plotly 
from plotly.offline.offline import _plot_html
from plotly.graph_objs import Scatter
import json
from django.core import serializers
from django.http import JsonResponse
from django.http import HttpResponse

class Stats(View):
    def get(self, request):
        params=dict()
        logs=ALog.objects.filter(dts__gt=timezone.now()-datetime.timedelta(hours=2)).order_by('-dts')
        params['logs']=logs
        #bfipc=BFEvent.objects.filter(bfodds__ip=True,bfodds__dtc__gt=timezone.now()-datetime.timedelta(minutes=30)).count()
        bfipc=BFEvent.objects.filter(dtc__gt=timezone.now()-datetime.timedelta(minutes=30)).count()
        params['bfipc']=bfipc
        lsipc=LSEvent.objects.filter(dtc__gt=timezone.now()-datetime.timedelta(minutes=30)).count()
        params['lsipc']=lsipc
        params['last_time_data_taken']=timezone.now()
        return render(request,'stats.html',params)

class MainInspect(View):
    def get(self, request):
        params=dict()
        template='champs.html'
        if request.method == 'GET':
            if 'cid' in request.GET:
                cid=int(request.GET['cid'])
                events=MEvent.objects.filter(champ__id=cid)
                params['champ']=MChamp.objects.get(id=cid)
                params['events']=events
                template='events.html'
            if 'evid' in request.GET and 'isip' in request.GET:
                meid=int(request.GET['evid'])
                isip=request.GET['isip']=='1'
                mevent=MEvent.objects.get(id=meid)
                lsevent=LSEvent.objects.filter(meid=mevent.meid)
                bfevent=BFEvent.objects.filter(meid=mevent.meid)
                params['mevent']=mevent
                if len(lsevent)==1 and isip:
                    lsev=lsevent[0]
                    params['lsevent']=lsev
                    setsn=LSGame.objects.filter(eid=lsev).aggregate(Max('setn'))
                    params['games']=[]
                    games=LSGame.objects.filter(eid=lsev, setn__lt=6).order_by('dtc')
                    for g in games:
                        points=LSPoint.objects.filter(gid=g).order_by('dtc')
                        params['games'].append([g,points])
                if len(bfevent)==1:
                    bfev=bfevent[0]
                    params['bfevent']=bfev
                    oddschanges=BFOdds.objects.filter(eid=bfev,ip=isip).order_by('dtc')
                    params['isip0']='' if isip else ' disabled'
                    params['isip1']=' disabled' if isip else ''
                    try:
                        goip=BFOdds.objects.filter(eid=bfev,ip=False).latest('dtc').dtc
                    except:
                        goip=''
                    params['goip']=goip
                    params['oddschanges']=oddschanges
                    plotly.tools.set_credentials_file(username='hwait', api_key='mYs3EJORl98E0vxkWvGr')
                    xr=[i.dtc for i in oddschanges]
                    y1r=[i.b1odds for i in oddschanges]
                    y2r=[i.b2odds for i in oddschanges]
                    figure_or_data = [Scatter(x=xr, y=y1r,mode = 'lines',name = bfev.pid1.name),Scatter(x=xr, y=y2r,mode = 'lines',name = bfev.pid2.name)]
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
                template='selected.html'
            else:
                params['cid']=''
                atp=MChamp.objects.filter(gender=1)
                wta=MChamp.objects.filter(gender=0)
                params['atp']=atp
                params['wta']=wta
        return render(request,template,params)

class ApiBind(View):
    def post(self, request):
        params=dict()
        pn=0
        en=0
        cn=0
        res='Ok'
        if 'champs' in request.POST:
            mchamps=json.loads(request.POST['champs'])
            for mchamp in mchamps:
                if BFChamp.objects.filter(id=int(mchamp['didbf'])).exists() or LSChamp.objects.filter(id=int(mchamp['didls'])).exists():
                    obj, created = MChamp.objects.get_or_create(mcid=int(mchamp['mcid']))
                    if (created):
                        obj.sport=2
                        obj.countryid=int(mchamp['countryid'])
                        obj.gender=int(mchamp['gender'])
                        obj.surface=int(mchamp['surface'])
                        obj.name=mchamp['name']
                        obj.prize=mchamp['prize']
                        obj.link=mchamp['link']
                        obj.save()
        if 'players' in request.POST:
            mplayers=json.loads(request.POST['players'])
            for mplayer in mplayers:
                obj, created = MPlayer.objects.get_or_create(mpid=int(mplayer['mpid']))
                if (created):
                    obj.gender=int(mplayer['gender'])
                    obj.name=mplayer['name']
                    obj.save()
        if 'events' in request.POST:
            mevents=json.loads(request.POST['events'])
            for mevent in mevents:
                isbf=BFEvent.objects.filter(id=int(mevent['didbf'])).exists()
                isls=LSEvent.objects.filter(id=int(mevent['didls'])).exists()
                isch=MChamp.objects.filter(mcid=int(mevent['mcid'])).exists()
                if isch and (isbf or isls):
                    champ=MChamp.objects.get(mcid=int(mevent['mcid']))
                    p1=MPlayer.objects.get(mpid=int(mevent['mpid1']))
                    p2=MPlayer.objects.get(mpid=int(mevent['mpid2']))
                    obj, created = MEvent.objects.get_or_create(meid=int(mevent['meid']))
                    if (created):
                        obj.champ=champ
                        obj.p1=p1
                        obj.p2=p2
                        obj.dt=timezone.make_aware(datetime.strptime(mevent['dt'], '%Y-%m-%dT%H:%M:%S'))
                        obj.save()
                    if isbf:
                        bf=BFEvent.objects.get(id=int(mevent['didbf']))
                        bf.reversed=int(mevent['revbf'])
                        bf.meid=int(mevent['meid'])
                        bf.save()
                    if isls:
                        ls=LSEvent.objects.get(id=int(mevent['didls']))
                        ls.reversed=int(mevent['revls'])
                        ls.meid=int(mevent['meid'])
                        ls.save()
        else:
            res='no data'
        response_data = {}
        response_data['result'] = res

        return HttpResponse(JsonResponse(response_data), content_type="application/json")
