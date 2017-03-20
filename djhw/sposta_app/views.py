from django.shortcuts import render
from django.views import View
from main_app.models import ALog
from sposta_app.models import MChamp, MPlayer,MEvent
from betfair_app.models import BFChamp,BFEvent,BFPlayer,BFOdds
from livescores.models import LSChamp,LSEvent,LSPlayer,LSGame,LSPoint
from oddsportal.models import OPChamp,OPEvent,OPPlayer,OPOdds
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Max
from betfair_app.models import BFEvent
from livescores.models import LSEvent
import plotly 
from plotly.offline.offline import _plot_html
from plotly.graph_objs import Scatter, Layout
import json
from django.core import serializers
from django.http import JsonResponse
from django.http import HttpResponse

class Stats(View):
    def get(self, request):
        params=dict()
        logs=ALog.objects.filter(dts__gt=timezone.now()-timedelta(hours=2)).order_by('-dts')
        params['logs']=logs
        #bfipc=BFEvent.objects.filter(bfodds__ip=True,bfodds__dtc__gt=timezone.now()-timedelta(minutes=30)).count()
        bfipc=BFEvent.objects.filter(dtc__gt=timezone.now()-timedelta(minutes=30)).count()
        params['bfipc']=bfipc
        lsipc=LSEvent.objects.filter(dtc__gt=timezone.now()-timedelta(minutes=30)).count()
        params['lsipc']=lsipc
        params['last_time_data_taken']=timezone.now()
        params['bfchamps']=BFChamp.objects.filter(bfevent__pk__isnull=True)
        params['lschamps']=LSChamp.objects.filter(lsevent__pk__isnull=True)
        return render(request,'stats.html',params)

class MainInspect(View):
    def get(self, request):
        params=dict()
        template='champs.html'
        if request.method == 'GET':
            if 'cid' in request.GET:
                cid=int(request.GET['cid'])
                events=MEvent.objects.select_related('p1','p2').filter(champ__id=cid).order_by('-dt')
                params['champ']=MChamp.objects.get(id=cid)
                params['events']=events
                template='events.html'
            if 'evid' in request.GET and 'sn' in request.GET:
                setsCount=1
                meid=int(request.GET['evid'])
                sn=int(request.GET['sn'])
                gid=0
                if 'gid' in request.GET:
                    gid=int(request.GET['gid'])
                    params['gid']=gid
                    currentgame=LSGame.objects.prefetch_related('lspoint_set').get(id=gid)
                mevent=MEvent.objects.select_related('p1','p2','champ').get(id=meid)
                params['mevent']=mevent
                setsCount=len(mevent.res.split(' '))
                params['champ']=mevent.champ
                params['player1']=mevent.p1
                params['player2']=mevent.p2
                lsevent=LSEvent.objects.prefetch_related('lsgame_set').filter(meid=mevent.meid)
                isls=len(lsevent)>0
                bfevent=BFEvent.objects.prefetch_related('bfodds_set').filter(meid=mevent.meid)
                isbf=len(bfevent)>0
                if sn==0: # OP data for Not In-Play only
                    opevent=OPEvent.objects.prefetch_related('opodds_set').filter(meid=mevent.meid)
                    isop=len(opevent)>0
                    if isop:
                        opev=opevent[0]
                        if isbf:
                            try:
                                lastbf=BFOdds.objects.filter(eid=bfevent[0],ip=0).latest('dtc').dtc
                                opchanges=OPOdds.objects.filter(ev=opev, dtc__lte=lastbf).order_by('dtc')
                            except:
                                opchanges=OPOdds.objects.filter(ev=opev).order_by('dtc')
                            xrop=[i.dtc_tz for i in opchanges]
                            y1rop=[i.w1 for i in opchanges]
                            y2rop=[i.w2 for i in opchanges]
                            y1ropm=[i.w1max for i in opchanges]
                            y2ropm=[i.w2max for i in opchanges]
                ts=None
                te=None
                gameshapes=[]
                if isls:
                    linestylegames=dict(color='rgb(128, 0, 128)',width=3,dash='dot')
                    linestylepoints=dict(color='rgb(128, 128, 128)',width=0.75)
                    lsev=lsevent[0]
                    params['lsevent']=lsev
                    shapespoint=[]
                    annos=[]
                    annospoint=[]
                    games=[]
                    if gid>0:
                        isfirstgame=currentgame.sc1==0 and currentgame.sc2==0 and currentgame.setn==1
                        islastgame=LSGame.objects.filter(eid=lsev, dtc__gt=currentgame.dtc).count()==1
                        currentpoints=LSPoint.objects.filter(gid=currentgame).order_by('dtc')
                        if not isfirstgame:
                            prevgame=LSGame.objects.filter(eid=lsev, dtc__lt=currentgame.dtc).latest('dtc')
                        currentgamestart=currentgame.dtc
                        nextgame=LSGame.objects.filter(eid=lsev, dtc__gt=currentgame.dtc).order_by('dtc')[0]
                        currentgameend=LSPoint.objects.filter(gid=nextgame).order_by('dtc')[0].dtc_tz
                        pts=LSPoint.objects.filter(gid=prevgame).order_by('-dtc')[1].dtc if not isfirstgame else currentgamestart-timedelta(seconds=60)
                        pte=LSPoint.objects.filter(gid=nextgame).order_by('dtc')[0].dtc if islastgame else LSPoint.objects.filter(gid=nextgame).order_by('dtc')[1].dtc
                        shapespoint.append(dict(type='rect',yref='paper',x0=timezone.make_naive(pts),y0=0,x1=currentgame.dtc_tz,y1=1,fillcolor='#ffccbc', opacity=0.3,line={'width': 0}))
                        shapespoint.append(dict(type='rect',yref='paper',x0=currentgameend,y0=0,x1=timezone.make_naive(pte),y1=1,fillcolor='#ffccbc', opacity=0.3,line={'width': 0}))
                        if lsev.reversed==0:
                            prevgametxt='Not IP' if isfirstgame else '%s*-%s'%(prevgame.sc1,prevgame.sc2) if prevgame.serve==1 else '%s-%s*'%(prevgame.sc1,prevgame.sc2)
                            currentgametxt='%s*-%s'%(currentgame.sc1,currentgame.sc2) if currentgame.serve==1 else '%s-%s*'%(currentgame.sc1,currentgame.sc2)
                            nextgametxt='' if islastgame else '%s*-%s'%(nextgame.sc1,nextgame.sc2) if nextgame.serve==1 else '%s-%s*'%(nextgame.sc1,nextgame.sc2)
                        else:
                            prevgametxt='Not IP' if isfirstgame else '%s-%s*'%(prevgame.sc2,prevgame.sc1) if prevgame.serve==1 else '%s*-%s'%(prevgame.sc2,prevgame.sc1)
                            currentgametxt='%s-%s*'%(currentgame.sc2,currentgame.sc1) if currentgame.serve==1 else '%s*-%s'%(currentgame.sc2,currentgame.sc1)
                            nextgametxt='' if islastgame else '%s-%s*'%(nextgame.sc2,nextgame.sc1) if nextgame.serve==1 else '%s*-%s'%(nextgame.sc2,nextgame.sc1)
                        annospoint.append(dict(x=currentgame.dtc_tz-timedelta(seconds=10),y=1,xref='x',yref='paper', showarrow=False,text=prevgametxt, textangle=-90, font=dict(family='verdana', size=14, color='#1f77b4'),opacity=0.7 ))
                        annospoint.append(dict(x=currentgameend+timedelta(seconds=10),y=1,xref='x',yref='paper', showarrow=False,text=nextgametxt, textangle=-90, font=dict(family='verdana', size=14, color='#1f77b4'),opacity=0.7 ))
                        for point in currentpoints:
                            shapespoint.append(dict(type='line',yref='paper',x0=point.dtc_tz,y0=0,x1=point.dtc_tz,y1=1,line=linestylepoints))
                            annospoint.append(dict(x=point.dtc_tz+timedelta(seconds=3),y=1,xref='x',yref='paper', showarrow=False,text=self.getPointText(point.sc1, point.sc2,lsev.reversed), textangle=-90,  font=dict(family='verdana', size=11, color='#1f77b4'),opacity=0.8 ))
                        shapespoint.append(dict(type='line',yref='paper',x0=currentgame.dtc_tz,y0=0,x1=currentgame.dtc_tz,y1=1,line=linestylegames))
                        shapespoint.append(dict(type='line',yref='paper',x0=currentgameend,y0=0,x1=currentgameend,y1=1,line=linestylegames))
                        gamelay=Layout(title=currentgametxt,shapes = shapespoint, annotations=annospoint,yaxis=dict(type='log', autorange=True),)

                    if(sn==0): # not IP
                        ts=LSGame.objects.filter(eid=lsev,setn=1).order_by('dtc')[0].dtc
                        te=LSGame.objects.filter(eid=lsev,setn=1).order_by('dtc')[1].dtc
                        gameshapes.append(dict(type='line',yref='paper',x0=timezone.make_naive(ts),y0=0,x1=timezone.make_naive(ts),y1=1,line=linestylegames))
                        gameshapes.append(dict(type='rect',yref='paper',x0=timezone.make_naive(ts),y0=0,x1=timezone.make_naive(te),y1=1,fillcolor='#ffccbc', opacity=0.3,line={'width': 0}))
                        if isbf:
                            bfchanges=BFOdds.objects.filter(eid=bfevent[0], dtc__lte=te,b1odds__gt=0,b2odds__gt=0,l1odds__gt=0,l2odds__gt=0).order_by('dtc')
                    elif(sn<setsCount): # First or Middle set
                        #gs=LSGame.objects.filter(eid=lsev,setn=sn-1).order_by('-dtc')[0].dtc
                        curgame=LSGame.objects.filter(eid=lsev,setn=sn).order_by('dtc')[0]
                        curgames=LSGame.objects.filter(eid=lsev,setn=sn).order_by('dtc')[0].dtc
                        gameshapes.append(dict(type='line',yref='paper',x0=timezone.make_naive(curgames),y0=0,x1=timezone.make_naive(curgames),y1=1,line=linestylegames))
                        ts=curgames-timedelta(seconds=900) if sn==1 else curgames
                        #if sn==1:
                        gameshapes.append(dict(type='rect',yref='paper',x0=timezone.make_naive(ts),y0=0,x1=timezone.make_naive(curgames),y1=1,fillcolor='#ffccbc', opacity=0.3,line={'width': 0}))
                        #else:
                        #    gameshapes.append(dict(type='rect',yref='paper',x0=ts,y0=0,x1=curgames,y1=1,fillcolor='#ffccbc', opacity=0.3,line={'width': 0}))
                        te=LSGame.objects.filter(eid=lsev,setn=sn+1).order_by('dtc')[1].dtc
                        ge=LSGame.objects.filter(eid=lsev,setn=sn+1).order_by('dtc')[0].dtc
                        games=LSGame.objects.prefetch_related('lspoint_set').filter(eid=lsev, setn__gt=0, dtc__gte=ts, dtc__lte=te).order_by('dtc')
                        if gid>0: 
                            ts=pts
                            te=pte
                        if isbf:
                            bfchanges=BFOdds.objects.filter(eid=bfevent[0], dtc__gte=ts, dtc__lte=te,b1odds__gt=0,b2odds__gt=0,l1odds__gt=0,l2odds__gt=0).order_by('dtc') 
                        gameshapes.append(dict(type='line',yref='paper',x0=timezone.make_naive(ge),y0=0,x1=timezone.make_naive(ge),y1=1,line=linestylegames))                        
                        gameshapes.append(dict(type='rect',yref='paper',x0=timezone.make_naive(ge),y0=0,x1=timezone.make_naive(te),y1=1,fillcolor='#ffccbc', opacity=0.3,line={'width': 0}))
                    else: # Last set
                        ts=LSGame.objects.filter(eid=lsev,setn=sn-1).order_by('-dtc')[0].dtc
                        endset=LSGame.objects.filter(eid=lsev,setn=6)
                        games=LSGame.objects.prefetch_related('lspoint_set').filter(eid=lsev, dtc__gte=ts, setn__lt=6).order_by('dtc')
                        te=games[1].dtc
                        if gid>0: 
                            ts=pts
                            te=endset[0].dtc if islastgame else pte
                        else:
                            gameshapes.append(dict(type='line',yref='paper',x0=timezone.make_naive(te),y0=0,x1=timezone.make_naive(te),y1=1,line=linestylegames))
                            gameshapes.append(dict(type='rect',yref='paper',x0=timezone.make_naive(ts),y0=0,x1=timezone.make_naive(te),y1=1,fillcolor='#ffccbc', opacity=0.3,line={'width': 0})) 
                            try:
                                te=endset[0].dtc
                            except:
                                te=BFOdds.objects.filter(eid=bfevent[0]).latest('dtc').dtc
                        if isbf:
                            bfchanges=BFOdds.objects.filter(eid=bfevent[0], dtc__gte=ts, dtc__lte=te,b1odds__gt=0,b2odds__gt=0,l1odds__gt=0,l2odds__gt=0).order_by('dtc') if len(endset)>0 or gid>0 else BFOdds.objects.filter(eid=bfevent[0], dtc__gte=ts,b1odds__gt=0,b2odds__gt=0,l1odds__gt=0,l2odds__gt=0).order_by('dtc')
                    params['games']=[]
                    if len(games)>0:
                        c=0
                        for g in games:
                            #points=LSPoint.objects.filter(gid=g).order_by('dtc')
                            params['games'].append(g)
                            if gid==0:
                                if lsev.reversed==0:
                                    gametxt='%s*-%s'%(g.sc1,g.sc2) if g.serve==1 else '%s-%s*'%(g.sc1,g.sc2)
                                else:
                                    gametxt='%s-%s*'%(g.sc2,g.sc1) if g.serve==1 else '%s*-%s'%(g.sc2,g.sc1)
                                if not (sn<setsCount and c==len(games)-1):
                                    annos.append(dict(x=games[c].dtc_tz+timedelta(seconds=30),y=1,xref='x',yref='paper', showarrow=False,text=gametxt, textangle=-90,  font=dict(family='verdana', size=12, color='#1f77b4'),opacity=0.8 ))
                                if g.serve==1 and c<len(games)-2 and c>0:
                                    gameshapes.append(dict(type='rect',yref='paper',x0=g.dtc_tz,y0=0,x1=games[c+1].dtc_tz,y1=1,fillcolor='#d3d3d3', opacity=0.3,line={'width': 0}))
                            c+=1
                    if (sn==0):
                        title='Not In-Play'
                    else:
                        title='Set #%s' % sn
                    lay=Layout(title=title,shapes = gameshapes, annotations=annos,yaxis=dict(type='log', autorange=True),)
                if isbf:
                    bfev=bfevent[0]
                    params['tscheduled']=bfev.dt
                    if mevent.res!='':
                        params['tcomplete']=bfev.dtc
                    if (ts==None and te==None):
                        bfchanges=BFOdds.objects.filter(eid=bfev,ip=0 if sn==0 else 1 ).order_by('dtc')
                    params=self.getSetButtons(params,sn,setsCount,isls)
                    try:
                        goip=BFOdds.objects.filter(eid=bfev,ip=False).latest('dtc').dtc_tz
                    except:
                        goip=''
                    params['goip']=goip
                    params['bfchanges']=bfchanges
                    plotly.tools.set_credentials_file(username='hwait', api_key='mYs3EJORl98E0vxkWvGr')
                    xr=[i.dtc_tz for i in bfchanges]
                    if bfev.reversed==0:
                        y1r=[i.b1odds for i in bfchanges]
                        y1rl=[i.l1odds for i in bfchanges]
                        y2r=[i.b2odds for i in bfchanges]
                        y2rl=[i.l2odds for i in bfchanges]
                        p1=bfev.pid1.name
                        p2=bfev.pid2.name
                    else:
                        y2r=[i.b1odds for i in bfchanges]
                        y2rl=[i.l1odds for i in bfchanges]
                        y1r=[i.b2odds for i in bfchanges]
                        y1rl=[i.l2odds for i in bfchanges]
                        p2=bfev.pid1.name
                        p1=bfev.pid2.name
                    dataseries=[]
                    dataseries.append(Scatter(x=xr, y=y1r,mode = 'lines',name = p1+' (Back)', line=dict( color='rgb(40, 53, 147)', )))
                    dataseries.append(Scatter(x=xr, y=y1rl,mode = 'lines',name = p1+' (Lay)', line=dict( color='rgb(121, 134, 203)', ),visible="legendonly"))
                    if sn==0 and isop:
                        dataseries.append(Scatter(x=xrop, y=y1rop,mode = 'lines',name = p1+' (Avg)', line=dict( color='rgb(46, 125, 50)', )))
                        dataseries.append(Scatter(x=xrop, y=y1ropm,mode = 'lines',name = p1+' (Max)', line=dict( color='rgb(142, 36, 170)', ),visible="legendonly"))
                    dataseries.append(Scatter(x=xr, y=y2r,mode = 'lines',name = p2+' (Back)', line=dict( color='rgb(216, 67, 21)', )))
                    dataseries.append(Scatter(x=xr, y=y2rl,mode = 'lines',name = p2+' (Lay)', line=dict( color='rgb(255, 138, 101)', ),visible="legendonly"))
                    if sn==0 and isop:
                        dataseries.append(Scatter(x=xrop, y=y2rop,mode = 'lines',name = p2+' (Avg)', line=dict( color='rgb(249, 168, 37)', )))
                        dataseries.append(Scatter(x=xrop, y=y2ropm,mode = 'lines',name = p2+' (Max)', line=dict( color='rgb(233, 30, 99)', ),visible="legendonly"))
                    if gid>0:
                        figure_or_data = { "data": dataseries, "layout":gamelay }
                    elif isls and sn>0:
                        figure_or_data = { "layout": lay, "data": dataseries }
                    else:
                        figure_or_data = { "data": dataseries, "layout":Layout(title='Non-IP',shapes = gameshapes,yaxis=dict(type='log', autorange=True),) }
                    config = {}
                    config['showLink'] = False
                    #config['layout'] = layout
                    plot_html = plot_html, plotdivid, width, height = _plot_html(
                        figure_or_data,config, False, '100%', 600, False)
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
                atp=MChamp.objects.filter(gender=1).order_by('name')
                wta=MChamp.objects.filter(gender=0).order_by('name')
                params['atp']=atp
                params['wta']=wta
        return render(request,template,params)

    def getSetButtons(self, params, sn,sets,isls):
        params['setn0']='' if sn!=0 else ' disabled'
        params['setn1']='' if sn!=1 else ' disabled'
        params['setn2']='' if sn!=2 else ' disabled'
        params['setn3']='' if sn!=3 else ' disabled'
        params['setn4']='' if sn!=4 else ' disabled'
        params['setn5']='' if sn!=5 else ' disabled'
        if sets==1:
            params['setn0']=' hidden'
            params['setn1']=' hidden'
            params['setn2']=' hidden'
        if sets<3:
            params['setn3']=' hidden' 
        if sets<4:
            params['setn4']=' hidden' 
        if sets<5:
            params['setn5']=' hidden' 
        if not isls:
            params['setn2']=' hidden'
            params['setn3']=' hidden'
        return params

    def point2string(self, sc):
        if sc==0:
            return '0'
        if sc==1:
            return '15'
        if sc==2:
            return '30'
        if sc==3:
            return '40'
        if sc==4:
            return 'A'

    def getPointText(self, sc1, sc2,reversed):
        if reversed==0:
            return '%s-%s'%(self.point2string(sc1),self.point2string(sc2))
        if reversed==1:
            return '%s-%s'%(self.point2string(sc2),self.point2string(sc1))

        return params

class ApiBind(View):
    def post(self, request):
        params=dict()
        pn=0
        en=0
        cn=0
        res='Completed with Ok'
        rawstr=request.body.decode('utf-8')
        if 'champs' in request.POST:
            mchamps=json.loads(request.POST['champs'])
            for mchamp in mchamps:
                if BFChamp.objects.filter(id=int(mchamp['didbf'])).exists() or LSChamp.objects.filter(id=int(mchamp['didls'])).exists() or OPChamp.objects.filter(id=int(mchamp['didop'])).exists():
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
                obj.cid=mplayer['cid']
                obj.db=timezone.make_aware(datetime.strptime(mplayer['db'], '%Y-%m-%dT%H:%M:%S'))
                obj.save()
        if 'events' in request.POST:
            mevents=json.loads(request.POST['events'])
            for mevent in mevents:
                isbf=BFEvent.objects.filter(id=int(mevent['didbf'])).exists()
                isls=LSEvent.objects.filter(id=int(mevent['didls'])).exists()
                isop=OPEvent.objects.filter(id=int(mevent['didop'])).exists()
                isch=MChamp.objects.filter(mcid=int(mevent['mcid'])).exists()
                if isch and (isbf or isls or isop):
                    champ=MChamp.objects.get(mcid=int(mevent['mcid']))
                    p1=MPlayer.objects.get(mpid=int(mevent['mpid1']))
                    p2=MPlayer.objects.get(mpid=int(mevent['mpid2']))
                    obj, created = MEvent.objects.get_or_create(meid=int(mevent['meid']))
                    if (created):
                        obj.champ=champ
                        obj.p1=p1
                        obj.p2=p2
                        obj.dt=timezone.make_aware(datetime.strptime(mevent['dt'], '%Y-%m-%dT%H:%M:%S'))
                    obj.res=mevent['res']
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
                    if isop:
                        op=OPEvent.objects.get(id=int(mevent['didop']))
                        op.reversed=int(mevent['revop'])
                        op.meid=int(mevent['meid'])
                        op.save()
        else:
            res='no data'
        response_data = {}
        response_data['result'] = res

        return HttpResponse(JsonResponse(response_data), content_type="application/json")

class ApiBindEvents(View):
    def post(self, request):
        rawstr=request.body.decode('utf-8')
        mevents=json.loads(rawstr)
        err=''
        for mevent in mevents:
            isme=MEvent.objects.filter(meid=int(mevent['meid'])).exists()
            if isme:
                isbf=BFEvent.objects.filter(id=int(mevent['didbf'])).exists()
                isls=LSEvent.objects.filter(id=int(mevent['didls'])).exists()
                isop=LSEvent.objects.filter(id=int(mevent['didop'])).exists()
                isch=MChamp.objects.filter(mcid=int(mevent['mcid'])).exists()
                if isch and (isbf or isls or isop):
                    champ=MChamp.objects.get(mcid=int(mevent['mcid']))
                    p1=MPlayer.objects.get(mpid=int(mevent['mpid1']))
                    p2=MPlayer.objects.get(mpid=int(mevent['mpid2']))
                    obj, created = MEvent.objects.get_or_create(meid=int(mevent['meid']))
                    if (created):
                        obj.champ=champ
                        obj.dt=timezone.make_aware(datetime.strptime(mevent['dt'], '%Y-%m-%dT%H:%M:%S'))
                    obj.res=mevent['res']
                    obj.p1=p1
                    obj.p2=p2
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
                    if isop:
                        op=LSEvent.objects.get(id=int(mevent['didop']))
                        op.reversed=int(mevent['revop'])
                        op.meid=int(mevent['meid'])
                        op.save()
            else:
                err+='mevent %s not found;' % mevent['meid']
        response_data = {}
        response_data['result'] = '%s mevents inserted %s' % (len(mevents),err)
        return HttpResponse(JsonResponse(response_data), content_type="application/json")
       