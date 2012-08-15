from django.core.management.base import NoArgsCommand
from django.conf import settings
from django.contrib.auth.models import User
from ui.models import *
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

class Command(NoArgsCommand):
    @transaction.commit_on_success
    def handle_noargs(self, **options):
        print 'dumping askers'
        User.objects.filter(username__startswith='ask').delete()
        User.objects.filter(username__startswith='guy').delete()
        print 'dumping answerers'
        User.objects.filter(username__startswith='wolfgang').delete()
        User.objects.filter(username__startswith='ans').delete()
        print 'dumping domains'
        Domain.objects.filter(short_name='data-tamer').delete()
        print 'dumping data tamer app'
        Application.objects.filter(name='data-tamer').delete()
