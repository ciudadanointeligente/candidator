from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from elections.views import ElectionDetailView

urlpatterns = patterns('',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    (r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(admin.site.urls)),

    (r'^profiles/', include('profiles.urls')),

    # django-registration urls, maps common registration urls to the ones in django.contrib.auth
    url(r'^accounts/', include('registration.urls')),


    url(r'^', include('elections.urls')),


    url(r'^(?P<my_user>[a-zA-Z0-9-]+)/(?P<election_slug>[a-zA-Z0-9-]+)/medianaranja/$', 'candidator.elections.views.medianaranja1',name='medianaranja1'),
    url(r'^(?P<user>[a-zA-Z0-9-]+)/(?P<election>[a-zA-Z0-9-]+)/medianaranja/$', 'candidator.elections.views.medianaranja2',name='medianaranja2'),


    (r'^$', direct_to_template, {'template': 'index.html'}),


)


from django.conf import settings
if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static( settings.USER_FILES, document_root=settings.STATIC_ROOT )
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
   )
