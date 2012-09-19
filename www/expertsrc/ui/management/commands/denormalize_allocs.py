from django.core.management.base import NoArgsCommand
from ui.dbaccess import *

class Command(NoArgsCommand):
    @transaction.commit_on_success
    def handle_noargs(self, **options):
        print 'denormalizing allocations table'
        denormalize_allocs()
        print 'done'
