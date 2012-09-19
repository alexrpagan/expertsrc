from django.core.management.base import NoArgsCommand
from django.db import connections, transaction
from ui.dbaccess import *

class Command(NoArgsCommand):
    @transaction.commit_on_success
    def handle_noargs(self, **options):
        cur = connections['default'].cursor()
        print 'creating allocations'
        cur.execute('select * from create_allocations(1, 5, false);')
        print 'done'
