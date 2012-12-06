from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('ui.views',
    url(r'^$', 'index'),
    url(r'^login/$', 'login_user'),
    url(r'^logout/$', 'logout_user'),
    url(r'^user/$', 'implicit_overview'),
    url(r'^user/overview/', 'global_user_overview'),
    url(r'^user/id/(?P<uid>\d+)/$', 'overview_by_uid'),
    url(r'^user/name/(?P<username>[\w\-\.\d]+)/$', 'overview'),
    url(r'^user/(?P<username>[\w\-\.\d]+)/update_profile/$', 'update_profile'),
    url(r'^user/(?P<username>[\w\-\.\d]+)/add_expertise/$', 'add_expertise'),
    url(r'^answer/$', 'answer_home'),
    url(r'^answer/(?P<domain_id>\d+)/next_question$', 'next_question'),
    url(r'^batches/$', 'user_batches'),                   
    url(r'^batch/check_new/$', 'check_for_new_batches'),
    url(r'^batch/(?P<batch_id>\d+)/overview/$', 'batch_overview'),
    url(r'^batch/(?P<batch_id>\d+)/allocate/$', 'batch_panel'),
    url(r'^batch/get_allocation_suggestions/$', 'get_allocation_suggestions'),
    url(r'^batch/commit_allocations/$', 'commit_allocations'),
    url(r'^import/schema-map/questions/$', 'import_schema_map_questions'),                  
    url(r'^import/schema-map/answers/$', 'import_schema_map_answers'),
    url(r'^review/$', 'review_home'),
    url(r'^review/next/$', 'next_review'),
    url(r'^tamer/$', 'redirect_to_tamer'),                   
    url(r'^about/$', 'about'),
    url(r'^thanks/$', 'thanks_and_goodbye'),
    url(r'^domain/$', 'domain_overview'),
    url(r'^domain/(?P<domain_id>\d+)/$', 'domain_details'),
    url(r'^domain/(?P<domain_id>\d+)/avail-data$', 'avail_data'),
    url(r'^domain/(?P<domain_id>\d+)/price-data$', 'price_data'),
)

urlpatterns += patterns('',
    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.STATIC_DOC_ROOT}),
    )
