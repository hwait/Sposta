from betfair_app.logic import BFCommand

class Command(BFCommand):
    help = 'Refreshes betfair NI data'

    def handle(self, *args, **options):
        self.betfair_get(False,0)