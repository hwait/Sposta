from django.core.management.base import BaseCommand, CommandError
from betfair_app.models import BFChamp,BFPlayer,BFEvent,BFOdds
from main_app.models import ALog
from datetime import datetime,timedelta
from django.utils import timezone
from betfair import Betfair
from betfair.models import MarketFilter,TimeRange,PriceProjection
import betfair.constants
from django.conf import settings
import requests

class BFCommand(BaseCommand):
    is_debug=True
    sports={ 'Soccer':1		
    ,'Tennis':2		
    ,'Golf':3		
    ,'Cricket':4		
    ,'Rugby Union':5		
    ,'Boxing':6		
    ,'Horse Racing':7		
    ,'Motor Sport':8		
    ,'Special Bets':9		
    ,'Handball':468328	
    ,'Winter Sports':451485	
    ,'Basketball':7522	
    ,'Rugby League':1477	
    ,'Greyhound Racing':4339	
    ,'Politics':19		
    ,'Financial Bets':6231	
    ,'Volleyball':99817	
    ,'Bowls':998918	
    ,'Bandy':998919	
    ,'Darts':3503	
    ,'Pool':72382	
    ,'Snooker':6422	
    ,'American Football':6423	
    ,'Baseball':7511}
    def betfair_get(self,is_ip,counter,sport='Tennis'):
        start=timezone.now()
        ip='ip' if is_ip else 'ni'
        
        client = Betfair('GkhXY3b3KmncnwLe', 'certs/bf.pem')
        client.login('sherst', 'osT1G11nRe35')
        client.keep_alive()
        tennis_event_type = self.sports[sport]
        markets = client.list_market_catalogue(
            MarketFilter(event_type_ids=[tennis_event_type], market_type_codes=["MATCH_ODDS"], in_play_only=is_ip),
                            market_projection=["EVENT", "RUNNER_METADATA","COMPETITION"],
                            max_results=1000)
        mids=[m.market_id for m in markets]
        mids_portions = [mids[x:x+40] for x in xrange(0, len(mids), 40)]
        for mp in mids_portions:
            print(','.join(mp))
            books=client.list_market_book(mp,price_projection=PriceProjection(price_data=betfair.constants.PriceData.EX_BEST_OFFERS))
            for b in books:
                m=next((x for x in markets if x.market_id==b.market_id), None)
                if m.competition==None: continue
                bfcid=m.competition.id
                champname=m.competition.name
                country=m.event.country_code
                event_id=m.event.id
                ds=timezone.make_aware(m.event.open_date)
                p1=m.runners[0].runner_name
                if('/' in p1): 
                    continue
                rid1=m.runners[0].selection_id
                p2=m.runners[1].runner_name
                rid2=m.runners[1].selection_id
                event, created = BFEvent.objects.get_or_create(bfid=event_id)
                if (created):
                    champ=self.save_champ(bfcid,champname,tennis_event_type,country)
                    player1=self.save_player(p1)
                    player2=self.save_player(p2)
                    event.cid=champ
                    event.rid1=rid1
                    event.rid2=rid2
                    event.pid1=player1
                    event.pid2=player2
                    event.dt=ds
                    event.status=1 if is_ip else 0
                    event.save()
                p1b1_odds=b.runners[0].ex.available_to_back[0].price if len(b.runners[0].ex.available_to_back)>0 else 0
                p1b1_size=b.runners[0].ex.available_to_back[0].size if len(b.runners[0].ex.available_to_back)>0 else 0
                p1l1_odds=b.runners[0].ex.available_to_lay[0].price if len(b.runners[0].ex.available_to_lay)>0 else 0
                p1l1_size=b.runners[0].ex.available_to_lay[0].size if len(b.runners[0].ex.available_to_lay)>0 else 0
                p2b1_odds=b.runners[1].ex.available_to_back[0].price if len(b.runners[1].ex.available_to_back)>0 else 0
                p2b1_size=b.runners[1].ex.available_to_back[0].size if len(b.runners[1].ex.available_to_back)>0 else 0
                p2l1_odds=b.runners[1].ex.available_to_lay[0].price if len(b.runners[1].ex.available_to_lay)>0 else 0
                p2l1_size=b.runners[1].ex.available_to_lay[0].size if len(b.runners[1].ex.available_to_lay)>0 else 0
                if (self.is_debug):
                    self.stdout.write('*** evid [%s] %s - %s at %s, changed %s\n' % (event.id,event.pid1.name,event.pid2.name,event.dt,event.dtc), ending='')
                try:
                    odds= BFOdds.objects.filter(eid=event).latest('dtc')
                    if(odds.b1odds!=p1b1_odds or odds.b2odds!=p2b1_odds or odds.l1odds!=p1l1_odds or odds.l2odds!=p2l1_odds):
                        self.save_odds(event,p1b1_odds,p2b1_odds,p1l1_odds,p2l1_odds,p1b1_size,p2b1_size,p1l1_size,p2l1_size,is_ip)
                        if (self.is_debug):
                            self.stdout.write('evid[%s], mid[%s] %s %s - %s in %s: %s/%s\n' % (event_id,b.market_id, ds,p1.replace('\\',''),p2.replace('\\',''),country,b.total_matched,b.total_available), ending='')
                            self.stdout.write('[%s]%s:%s@%s\t|%s@%s\n' % (rid1,p1.replace('\\',''), p1b1_size,p1b1_odds,p1l1_size,p1l1_odds), ending='')
                            self.stdout.write('[%s]%s:%s@%s\t|%s@%s\n' % (rid2,p2.replace('\\',''), p2b1_size,p2b1_odds,p2l1_size,p2l1_odds), ending='')
                except:
                    self.save_odds(event,p1b1_odds,p2b1_odds,p1l1_odds,p2l1_odds,p1b1_size,p2b1_size,p1l1_size,p2l1_size,is_ip)
                    if (self.is_debug):
                        self.stdout.write('evid[%s], mid[%s] %s %s - %s in %s: %s/%s\n' % (event_id,b.market_id, ds,p1.replace('\\',''),p2.replace('\\',''),country,b.total_matched,b.total_available), ending='')
                        self.stdout.write('[%s]%s:%s@%s\t|%s@%s\n' % (rid1,p1.replace('\\',''), p1b1_size,p1b1_odds,p1l1_size,p1l1_odds), ending='')
                        self.stdout.write('[%s]%s:%s@%s\t|%s@%s\n' % (rid2,p2.replace('\\',''), p2b1_size,p2b1_odds,p2l1_size,p2l1_odds), ending='')
        end=timezone.now()
        log=ALog()
        log.name='update_bf_%s_%s' % (sport,ip)
        log.dts=start
        log.counter=counter
        log.duration=(end-start).total_seconds()
        log.save()
        if (self.is_debug):
            self.stdout.write('total execution is %s seconds\n' %(end-start), ending='')

    def save_champ(self,bfcid,name,sport,country_code):
        champ, created = BFChamp.objects.get_or_create(bfid=bfcid)
        if (created):
            if (self.is_debug):
                self.stdout.write('created a new champ, id=%s\n' % (champ.id), ending='')
                champ.sport=sport
                champ.name=name
                champ.country_code=country_code
                champ.save()
        return champ

    def save_player(self,name):
        player, created = BFPlayer.objects.get_or_create(name=name)
        return player

    def save_odds(self,eid,p1b1_odds,p2b1_odds,p1l1_odds,p2l1_odds,p1b1_size,p2b1_size,p1l1_size,p2l1_size,is_ip):
        dtc=timezone.now()
        odds=BFOdds()
        odds.eid=eid
        odds.b1odds=p1b1_odds
        odds.b2odds=p2b1_odds
        odds.l1odds=p1l1_odds
        odds.l2odds=p2l1_odds
        odds.b1size=p1b1_size
        odds.b2size=p2b1_size
        odds.l1size=p1l1_size
        odds.l2size=p2l1_size
        odds.ip=is_ip
        odds.dtc=dtc
        odds.save()
        eid.dtc=dtc
        eid.save()