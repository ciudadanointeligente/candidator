from django.conf.urls.defaults import patterns, url
from django.views.generic import DetailView, ListView

from models import Election

urlpatterns = patterns('',
    url(r'^election/(?P<pk>\d+)/$',
        DetailView.as_view(model=Election),
        name='election_detail'),
    url(r'^$', ListView.as_view(model=Election), name='election_list'),
)
