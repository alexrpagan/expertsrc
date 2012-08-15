from django.core.management.base import NoArgsCommand
from ui.models import *
from django.db import connections, transaction
from django.conf import settings
import redis

class Command(NoArgsCommand):
    @transaction.commit_on_success
    def handle_noargs(self, **options):
        cur = connections[settings.TAMER_DB].cursor()
        print 'clear loaded data sources from remote database.'
        cur.execute('select * from unload_local()')
        cur.connection.commit()

        print 'flush the message queue'
        r = redis.Redis()
        r.delete('question')
        r.delete('answer')
        r.delete('review')
        
        print 'delete the guy who owns all of the schema mapping questions'
        User.objects.filter(username='data-tamer').delete()

        print 'recreate data-tamer user'
        dt = User.objects.create_user('data-tamer', '', 'test')
        dt.save()
        profile = UserProfile(user=dt,
                              user_class='ASK',
                              bank_balance=1000)
        profile.save()
