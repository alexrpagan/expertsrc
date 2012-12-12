from django.db import connections
from django.conf import settings

class SearchPath:
    """ This is a hack that allows the db user's search path to be
    modified arbitrarily by datatamer while still ensuring that django
    can find its tables in the public schema.""" 
    def process_request(self, request):
        """ set schema_path to public (for good measure)"""
        cursor = connections["default"].cursor()
        cursor.execute("SET search_path TO public")
        return None

# context processors...

def url_context(request):
    alt_root = ''
    if settings.ALT_ROOT:
        alt_root = ''.join(('/', settings.ALT_ROOT,))
    return { 'base_url': settings.BASE_URL,
             'alt_root': alt_root }
