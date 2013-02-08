from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template, redirect_to

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from tastypie.api import Api


admin.autodiscover()


urlpatterns = patterns('',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    (r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(admin.site.urls)),

    (r'^profiles/', include('profiles.urls')),

    # django-registration urls, maps common registration urls to the ones in django.contrib.auth
    url(r'^accounts/', include('registration.urls')),

    url(r'^accounts/password_reset/?$','django.contrib.auth.views.password_reset'),

    url(r'^report/', include('report_objects.urls')),

    (r'^api/', include('elections.api_urls')),

    url(r'^', include('elections.urls')),



    

    # url(r'^index/?$', direct_to_template, {'template': 'index.html'}), # DESCOMENTAR CUANDO SE DEFINA UN INDEX

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
