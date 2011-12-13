from django.conf.urls.defaults import patterns, url
from django.views.generic import DetailView

from views import ReportCreateView
from models import Report


urlpatterns = patterns('',
    # Create Report
    url(r'^(?P<content_type>\d+)/(?P<object_id>\d+)/?$', ReportCreateView.as_view(), name='report'),
    # Detail Report
    url(r'^(?P<pk>\d+)/?$', DetailView.as_view(model=Report), name='report_detail'),
)
