from django.db import connections

class SearchPath:
    """ This is a hack that allows the db user's search path to be
    modified arbitrarily by datatamer while still ensuring that django
    can find its tables in the public schema.""" 
    def process_request(self, request):
        """ set schema_path to public (for good measure)"""
        cursor = connections["default"].cursor()
        cursor.execute("SET search_path TO public")
        return None
