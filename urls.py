from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'candidator.views.home', name='home'),
    # url(r'^candidator/', include('candidator.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(admin.site.urls)),

    (r'^profiles/', include('profiles.urls')),

    url(r'^elections/', include('elections.urls')),
    url(r'^(?P<my_user>[a-zA-Z0-9-]+)/(?P<election_slug>[a-zA-Z0-9-]+)/medianaranja/$', 'candidator.elections.views.medianaranja1',name='medianaranja1'),

)
