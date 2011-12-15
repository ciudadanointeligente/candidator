from django.conf.urls.defaults import patterns, url
from django.views.generic import DetailView, ListView, TemplateView, CreateView

from models import Election
from views import associate_answer_to_candidate, ElectionCreateView,\
                  ElectionUpdateView, ElectionDetailView, CandidateDetailView,\
                  CandidateCreateView, CandidateUpdateView, CategoryCreateView,\
                  CategoryUpdateView, PersonalDataCreateView,\
                  BackgroundCategoryCreateView, BackgroundCreateView, QuestionCreateView,\
                  AnswerCreateView, personal_data_candidate_create, background_candidate_create, MyElectionListView


urlpatterns = patterns('',

    # Root
    url(r'^elections/?$', ListView.as_view(model=Election), name='election_list'),

    # My Elections
    url(r'^(?P<username>[-\w]+)/my_elections/?$', login_required(MyElectionListView.as_view()), name='my_election_list'),

    # Associate Candidate
    url(r'^(?P<election_slug>[-\w]+)/(?P<candidate_slug>[-\w]+)/associate_answers/',
            associate_answer_to_candidate,
            name='associate_answer_candidate'),

    # Create Category View
    url(r'^(?P<election_slug>[-\w]+)/category/create/?$', CategoryCreateView.as_view(), name='category_create'),

    # Update Category view
    url(r'^(?P<election_slug>[-\w]+)/category/(?P<slug>[-\w]+)/update/?$', CategoryUpdateView.as_view(), name='category_update'),

    # Create Question view
    url(r'^(?P<category_pk>[0-9]+)/question/create/?$', QuestionCreateView.as_view(), name='question_create'),

    # Create Answer view
    url(r'^(?P<question_pk>[0-9]+)/answer/create/?$', AnswerCreateView.as_view(), name='answer_create'),

    # Create election view
    url(r'^election/create/?$', ElectionCreateView.as_view(), name='election_create'),

    # Election update view
    url(r'^election/(?P<slug>[-\w]+)/update/?$', ElectionUpdateView.as_view(), name='election_update'),

    # Election detail view
    url(r'^(?P<username>[-\w]+)/(?P<slug>[-\w]+)/$', ElectionDetailView.as_view(), name='election_detail'),

    # Election detail view admin
    url(r'^(?P<username>[-\w]+)/(?P<slug>[-\w]+)/admin$', ElectionDetailView.as_view(template_name='elections/election_detail_admin.html'), name='election_detail_admin'),

    # Election candidates profiles
    url(r'^(?P<username>[-\w]+)/(?P<slug>[-\w]+)/profiles$', ElectionDetailView.as_view(template_name='elections/election_detail_profiles.html'), name='election_detail_profiles'),

    # Election compare view
    url(r'^(?P<username>[-\w]+)/(?P<slug>[-\w]+)/compare$', 'candidator.elections.views.election_compare_view', name='election_compare'),

    # Election compare view with 1 candidate
    url(r'^(?P<username>[-\w]+)/(?P<slug>[-\w]+)/compare/(?P<first_candidate_slug>[-\w]+)$', 'candidator.elections.views.election_compare_view_one_candidate', name='election_compare_one_candidate'),

    # Election compare view with both candidates (and considering one category)
    url(r'^(?P<username>[-\w]+)/(?P<slug>[-\w]+)/compare/(?P<first_candidate_slug>[-\w]+)_vs_(?P<second_candidate_slug>[-\w]+)_in_(?P<category_slug>[-\w]+)$', 'candidator.elections.views.election_compare_view_two_candidates', name='election_compare_two_candidates'),

    # Update candidate view
    url(r'^(?P<election_slug>[-\w]+)/candidate/(?P<slug>[-\w]+)/update/?$', CandidateUpdateView.as_view(), name='candidate_update'),

    # Create candidate view
    url(r'^(?P<election_slug>[-\w]+)/candidate/create/?$', CandidateCreateView.as_view(), name='candidate_create'),

    # Create PersonalData
    url(r'^(?P<election_slug>[-\w]+)/personal_data/create/?$', PersonalDataCreateView.as_view(), name='personal_data_create'),

    # Create PersonalDataCandidate
    url(r'^(?P<candidate_pk>[0-9]+)/(?P<personal_data_pk>[0-9]+)/personal_data_associate' , personal_data_candidate_create, name='personal_data_candidate_create'),

    # Create BackgroundCategory
    url(r'^(?P<election_slug>[-\w]+)/background_category/create/?$', BackgroundCategoryCreateView.as_view(), name='background_category_create'),

    # Create Background
    url(r'^(?P<background_category_pk>[0-9]+)/background/create/?$', BackgroundCreateView.as_view(), name='background_create'),

    # Create BackgroundCandidate
    url(r'^(?P<candidate_pk>[0-9]+)/(?P<background_pk>[0-9]+)/background_associate' , background_candidate_create, name='background_candidate_create'),

    # Media Naranja
    url(r'^(?P<username>[a-zA-Z0-9-]+)/(?P<election_slug>[a-zA-Z0-9-]+)/medianaranja$', 'candidator.elections.views.medianaranja1',name='medianaranja1'),

    # Candidate detail view
    url(r'^(?P<username>[-\w]+)/(?P<election_slug>[-\w]+)/(?P<slug>[-\w]+)$', CandidateDetailView.as_view(), name='candidate_detail'),

)
