from django.core.management.base import NoArgsCommand
from django.conf import settings
from django.contrib.auth.models import User 
from ui.models import *
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

class Command(NoArgsCommand):
    @transaction.commit_on_success
    def handle_noargs(self, **options):

        with open('/home/apagan/users.txt', 'r') as f:
            user_list = f.read()        
        lines = user_list.split('\n')
        for line in lines:
            split_email = line.split('@');
            if split_email[0]:
                print 'deleting user: %s' % split_email[0]
                try:
                    User.objects.get(username=split_email[0]).delete()
                except Exception, e:
                    print 'failed...'
                    print e

        print 'dumping domains'
        Domain.objects.filter(short_name='pharon-assay').delete()

        print 'dumping data tamer app'
        Application.objects.filter(name='data-tamer').delete()
