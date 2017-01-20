from betfair_app.logic import BFCommand
from livescores.logic import RepeatedTimer
from django.conf import settings
from django.utils import timezone

class Command(BFCommand):
    help = 'Refreshes betfair IP data'
    counter=0
    gstart=timezone.now()
    timeout=7
    duration=3600
    is_debug=True

    def handle(self, *args, **options):
        self.max_attempts=int(self.duration*60/self.timeout)
        self.timer = RepeatedTimer(self.timeout, self.reload, True)
        #self.betfair_get(True)

    def reload(self, is_ip):
        if (self.is_debug):
            self.stdout.write('#%s (%s sec):\n' %(self.counter,self.duration-((timezone.now()-self.gstart).total_seconds()+self.timeout)), ending='')
        self.betfair_get(is_ip,self.counter)
        if (timezone.now()-self.gstart).total_seconds()+self.timeout*3>=self.duration:
            self.timer.stop()
        # if self.counter>=self.max_attempts:
        #    self.timer.stop()
        self.counter+=1