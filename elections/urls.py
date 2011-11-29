
from django.conf.urls.defaults import patterns, url
from django.views.generic import DetailView, ListView, TemplateView

from models import Election
from views import associate_answer_to_candidate, ElectionCreateView, ElectionUpdateView, ElectionDetailView, CandidateDetailView, CandidateCreateView, CandidateUpdateView, CategoryCreateView

urlpatterns = patterns('',

    # Root
    url(r'^$', ListView.as_view(model=Election), name='election_list'),

    # Associate Candidate
    url(r'^(?P<election_slug>[-\w]+)/(?P<candidate_slug>[-\w]+)/associate_answers/',
            associate_answer_to_candidate,
            name='associate_answer_candidate'),

    # Create Category View
    url(r'^(?P<election_slug>[-\w]+)/category/create/?$', CategoryCreateView.as_view(), name='category_create'),

    # Create election view
    url(r'^election/create/?$', ElectionCreateView.as_view(), name='election_create'),

    # Election detail view
    url(r'^(?P<username>[-\w]+)/(?P<slug>[-\w]+)/?$', ElectionDetailView.as_view(), name='election_detail'),

    # Update candidate view
    url(r'^(?P<election_slug>[-\w]+)/(?P<slug>[-\w]+)/update/?$', CandidateUpdateView.as_view(), name='candidate_update'),

    # Election update view
    url(r'^election/(?P<slug>[-\w]+)/update/?$', ElectionUpdateView.as_view(), name='election_update'),

    # Create candidate view
    url(r'^(?P<election_slug>[-\w]+)/candidate/create/?$', CandidateCreateView.as_view(), name='candidate_create'),

    # Media Naranja
    url(r'^(?P<username>[a-zA-Z0-9-]+)/(?P<election_slug>[a-zA-Z0-9-]+)/medianaranja/?$', 'candidator.elections.views.medianaranja1',name='medianaranja1'),
    url(r'^(?P<username>[a-zA-Z0-9-]+)/(?P<election_slug>[a-zA-Z0-9-]+)/medianaranja/?$', 'candidator.elections.views.medianaranja2',name='medianaranja2'),

    # Candidate detail view
    url(r'^(?P<username>[-\w]+)/(?P<election_slug>[-\w]+)/(?P<slug>[-\w]+)/?$', CandidateDetailView.as_view(), name='candidate_detail'),
)
