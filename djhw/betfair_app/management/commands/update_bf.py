from betfair_app.logic import BFCommand
import sys

class Command(BFCommand):
    help = 'Refreshes betfair NI data'

    def handle(self, *args, **options):
        self.betfair_get(False,0)
        sys.exit()
