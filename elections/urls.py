from django.conf.urls.defaults import patterns, url
from django.views.generic import DetailView, ListView

from models import Election
from views import associate_answer_to_candidate

urlpatterns = patterns('',
    url(r'^election/(?P<pk>\d+)/$',
        DetailView.as_view(model=Election),
        name='election_detail'),
    url(r'^$', ListView.as_view(model=Election), name='election_list'),

    url(r'^(?P<election_slug>\w+)/(?P<slug>\w+)/associate_answers/', 
            associate_answer_to_candidate,
            name='associate_answer_candidate'),

)
