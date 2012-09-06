from django.core.management.base import NoArgsCommand
from ui.dbaccess import *

class Command(NoArgsCommand):
    @transaction.commit_on_success
    def handle_noargs(self, **options):
        print 'creating prices'
        res = update_prices()
        print res
        print 'done'
