from django.core.management.base import NoArgsCommand
from ui.models import *
from django.db import connections, transaction
from django.conf import settings

class Command(NoArgsCommand):
    @transaction.commit_on_success
    def handle_noargs(self, **options):
        #cur = connections[settings.TAMER_DB].cursor()
        #print 'clear loaded data sources from remote database.'
        #ur.execute('select * from unload_local()')
        #cur.connection.commit()

        print 'delete the guy who owns all of the schema mapping questions'
        User.objects.filter(username='data-tamer').delete()

        print 'recreate data-tamer user'
        dt = User.objects.create_user('data-tamer', '', 'test')
        dt.save()
        profile = UserProfile(user=dt,
                              user_class='ASK',
                              bank_balance=100000)
        profile.save()
