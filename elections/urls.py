from django.conf.urls.defaults import patterns, url
from django.views.generic import DetailView, ListView, TemplateView

from models import Election
from views import associate_answer_to_candidate, add_category, ElectionCreateView, ElectionDetailView

urlpatterns = patterns('',
    url(r'^election/(?P<pk>\d+)/$',
        DetailView.as_view(model=Election),
        name='election_detail'),
    url(r'^$', ListView.as_view(model=Election), name='election_list'),

    url(r'^medianaranja1/$', 'elections.views.medianaranja1'),

    url(r'^(?P<election_slug>[-\w]+)/(?P<slug>[-\w]+)/associate_answers/',
            associate_answer_to_candidate,
            name='associate_answer_candidate'),

    url(r'^(?P<election_slug>[-\w]+)/add_category/', add_category, name='add_category' ),

    url(r'^election/create$', ElectionCreateView.as_view(), name='election_create'),
    url(r'^(?P<username>[-\w]+)/(?P<slug>[-\w]+)$', ElectionDetailView.as_view(), name='election_detail'),
    # TODO: modify to create candidate view
    url(r'^(?P<slug>[-\w]+)/candidate/create/$', TemplateView.as_view(template_name='404.html'), name='candidate_create')
)
