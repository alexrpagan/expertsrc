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
    url(r'^user/name/(?P<username>[\w-]+)/$', 'overview'),
    url(r'^user/(?P<username>[\w-]+)/update_profile/$', 'update_profile'),
    url(r'^user/(?P<username>[\w-]+)/add_expertise/$', 'add_expertise'),
    url(r'^answer/$', 'answer_home'),
    url(r'^answer/next_question/$', 'next_question'),
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
    url(r'^update_prices/$', 'update_prices'),
)

urlpatterns += patterns('',
    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.STATIC_DOC_ROOT}),
    )
