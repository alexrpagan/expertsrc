from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('ui.views',
    url(r'^$', 'index', 
        name='index'),
    url(r'^login/$', 'login_user', 
        name='login'),
    url(r'^logout/$', 'logout_user', 
        name='logout'),
    url(r'^user/$', 'implicit_overview', 
        name='resolve_user'),
    url(r'^user/overview/', 'global_user_overview', 
        name='global_user_overview'),
    url(r'^user/id/(?P<uid>\d+)/$', 'overview_by_uid', 
        name='user_by_id'),
    url(r'^user/name/(?P<username>[\w\-\.\d]+)/$', 'overview', 
        name='user_by_name' ),
    url(r'^user/(?P<username>[\w\-\.\d]+)/update_profile/$', 'update_profile', 
        name='update_profile'),
    url(r'^user/(?P<username>[\w\-\.\d]+)/add_expertise/$', 'add_expertise', 
        name='add_expertise'),
    url(r'^answer/(?P<domain_id>\d+)/next_question$', 'next_question', 
        name='next_question'),
    url(r'^batches/$', 'user_batches', 
        name='user_batches'),                   
    url(r'^batch/check_new/$', 'check_for_new_batches', 
        name='check_for_new_batches'),
    url(r'^batch/(?P<batch_id>\d+)/overview/$', 'batch_overview', 
        name='batch_overview'),
    url(r'^batch/(?P<batch_id>\d+)/allocate/$', 'batch_panel', 
        name='allocate_batch'),
    url(r'^batch/get_allocation_suggestions/$', 'get_allocation_suggestions', 
        name='get_allocation_suggestions'),
    url(r'^batch/commit_allocations/$', 'commit_allocations', 
        name='commit_allocations'),
    url(r'^import/schema-map/questions/$', 'import_schema_map_questions', 
        name='import_schema_map_questions'), 
    url(r'^tamer/$', 'redirect_to_tamer', 
        name='redirect_to_tamer'), 
    url(r'^about/$', 'about', 
        name='about'),
    url(r'^thanks/$', 'thanks_and_goodbye', 
        name='thanks'),
    url(r'^domain/$', 'domain_overview', 
        name='domain'),
    url(r'^domain/(?P<domain_id>\d+)/$', 'domain_details', 
        name='domain_details'),
    url(r'^domain/(?P<domain_id>\d+)/avail-data$', 'avail_data', 
        name='avail_data'),
    url(r'^domain/(?P<domain_id>\d+)/price-data$', 'price_data', 
        name='price_data'),
)

urlpatterns += patterns('',
    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.STATIC_DOC_ROOT}),
    )
