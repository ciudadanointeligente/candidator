from django.conf.urls.defaults import patterns, url
from django.views.generic import DetailView, ListView, TemplateView, CreateView
from django.contrib.auth.decorators import login_required
from elections.views.answer_views import AnswerCreateAjaxView

from models import Election
from views import associate_answer_to_candidate, ElectionCreateView,\
                  ElectionUpdateView, ElectionDetailView, CandidateDetailView,\
                  CandidateCreateView, CandidateUpdateView, CategoryCreateView,\
                  CandidateCreateAjaxView, CategoryUpdateView, PersonalDataCreateView,\
                  BackgroundCategoryCreateView, BackgroundCreateView, QuestionCreateView,\
                  AnswerCreateView, personal_data_candidate_create, background_candidate_create,\
                  candidate_data_update, async_delete_candidate, background_ajax_create, \
                  async_delete_background, async_delete_background_category, PrePersonalDataView


urlpatterns = patterns('',

    # Root: login_required (por ahora pues no se ha definido un index)
    url(r'^elections/?$', login_required(ListView.as_view(model=Election)), name='election_list'),

    # My Elections
    url(r'^my_elections/?$', login_required(TemplateView.as_view(template_name="elections/my_election_list.html")), name='my_election_list'),

    # Associate Candidate
    url(r'^(?P<election_slug>[-\w]+)/(?P<candidate_slug>[-\w]+)/associate_answers/',
            associate_answer_to_candidate,
            name='associate_answer_candidate'),

    # Create Answer Ajax
    url(r'answer_create/(?P<question_pk>\d+).json', AnswerCreateAjaxView.as_view(), name='answer_create_ajax'),

    # Estaba al final, cual queda?
    # Create Answer Ajax
    # url(r'^(?P<question_pk>[0-9]+)/answer/ajax_create/?$', answer_ajax_create, name='answer_ajax_create'),


    # Create Category View
    url(r'^(?P<election_slug>[-\w]+)/category/create/?$', CategoryCreateView.as_view(), name='category_create'),

    # Update Category view
    url(r'^(?P<election_slug>[-\w]+)/category/(?P<slug>[-\w]+)/update/?$', CategoryUpdateView.as_view(), name='category_update'),

    # Create Question view
    url(r'^(?P<election_slug>[-\w]+)/question/create/?$', QuestionCreateView.as_view(), name='question_create'),

    # Create Answer view
    url(r'^(?P<question_pk>[0-9]+)/answer/create/?$', AnswerCreateView.as_view(), name='answer_create'),

    # Create election view
    url(r'^election/create/?$', ElectionCreateView.as_view(), name='election_create'),

    # Pre-Create election view
    url(r'^election/pre_create/?$', login_required(TemplateView.as_view(template_name="elections/election_pre_create.html")), name='election_pre_create'),

    # Election update view
    url(r'^election/(?P<slug>[-\w]+)/update/?$', ElectionUpdateView.as_view(), name='election_update'),

    # Election detail view
    url(r'^(?P<username>[-\w]+)/(?P<slug>[-\w]+)/$', ElectionDetailView.as_view(), name='election_detail'),

    # Election detail view admin
    url(r'^(?P<username>[-\w]+)/(?P<slug>[-\w]+)/admin$', ElectionDetailView.as_view(template_name='elections/election_detail_admin.html'), name='election_detail_admin'),

    # Election candidates profiles
    url(r'^(?P<username>[-\w]+)/(?P<slug>[-\w]+)/profiles$', ElectionDetailView.as_view(template_name='elections/election_detail_profiles.html'), name='election_detail_profiles'),

    # Election compare view
    url(r'^(?P<username>[-\w]+)/(?P<slug>[-\w]+)/compare/?$', 'candidator.elections.views.election_compare_view', name='election_compare'),

    # Election compare view with both candidates (and considering one category)
    url(r'^(?P<username>[-\w]+)/(?P<slug>[-\w]+)/compare/(?P<first_candidate_slug>[-\w]+)/(?P<second_candidate_slug>[-\w]+)/(?P<category_slug>[-\w]+)/?$', 'candidator.elections.views.election_compare_view_two_candidates', name='election_compare_two_candidates'),

    # Election compare view with 1 candidate
    url(r'^(?P<username>[-\w]+)/(?P<slug>[-\w]+)/compare/(?P<first_candidate_slug>[-\w]+)/?$', 'candidator.elections.views.election_compare_view_one_candidate', name='election_compare_one_candidate'),

    # Asynchronous call for compare view
    #url(r'^(?P<username>[-\w]+)/(?P<slug>[-\w]+)/compare/async-call/(?P<candidate_slug>[-\w]+)/?$', 'candidator.elections.views.election_compare_asynchronous_call', name='election_compare_asynchronous_call'),






    # Update candidate view
    url(r'^(?P<election_slug>[-\w]+)/candidate/(?P<slug>[-\w]+)/update/?$', CandidateUpdateView.as_view(), name='candidate_update'),

    # Create candidate view
    url(r'^(?P<election_slug>[-\w]+)/candidate/create/?$', CandidateCreateView.as_view(), name='candidate_create'),

    # Create candidate using next button
    url(r'^(?P<election_slug>[-\w]+)/candidate/save_candidate/?$', CandidateCreateAjaxView.as_view(), name='async_create_candidate'),

    # Delete candidate view in wizzard
    url(r'^(?P<candidate_pk>[-\d]+)/candidate/async_delete/?$', 'candidator.elections.views.async_delete_candidate' , name='async_delete_candidate'),

    # Candidate data Update (PersonalData and Background)
    url(r'^(?P<election_slug>[-\w]+)/candidate/(?P<slug>[-\w]+)/data_update/?$', candidate_data_update, name='candidate_data_update'),

    # Pre-Create PersonalData
    url(r'^(?P<election_slug>[-\w]+)/pre_personaldata/?$', login_required(PrePersonalDataView.as_view(template_name="elections/pre_personaldata.html")), name='pre_personaldata'),

    # Create PersonalData
    url(r'^(?P<election_slug>[-\w]+)/personal_data/create/?$', PersonalDataCreateView.as_view(), name='personal_data_create'),

    # Delete personalData view in wizzard
    url(r'^(?P<personal_data_pk>[-\d]+)/personal_data/async_delete/?$', 'candidator.elections.views.async_delete_personal_data', name='async_delete_personal_data'),

    # Create PersonalDataCandidate
    url(r'^(?P<candidate_pk>[0-9]+)/(?P<personal_data_pk>[0-9]+)/personal_data_associate' , personal_data_candidate_create, name='personal_data_candidate_create'),

    # Create BackgroundCategory
    url(r'^(?P<election_slug>[-\w]+)/background_category/create/?$', BackgroundCategoryCreateView.as_view(), name='background_category_create'),

     # Delete BackgroundCategory view in wizzard
    url(r'^(?P<category_pk>[-\d]+)/background_category/async_delete/?$', 'candidator.elections.views.async_delete_background_category' , name='async_delete_background_category'),

    # Create Background
    url(r'^(?P<background_category_pk>[0-9]+)/background/create/?$', BackgroundCreateView.as_view(), name='background_create'),

    # Create Background Ajax
    url(r'^(?P<background_category_pk>[0-9]+)/background/ajax_create/?$', background_ajax_create, name='background_ajax_create'),

    # Delete background view in wizzard
    url(r'^(?P<background_pk>[-\d]+)/background/async_delete/?$', 'candidator.elections.views.async_delete_background' , name='async_delete_background'),

    # Delete category view in wizzard
    url(r'^(?P<category_pk>[0-9]+)/category/async_delete/?$', 'candidator.elections.views.async_delete_category' , name='async_delete_category'),

    # Create BackgroundCandidate
    url(r'^(?P<candidate_pk>[0-9]+)/(?P<background_pk>[0-9]+)/background_associate' , background_candidate_create, name='background_candidate_create'),

    # Delete question view in wizzard
    url(r'^(?P<question_pk>[0-9]+)/question/async_delete/?$', 'candidator.elections.views.async_delete_question' , name='async_delete_question'),

    # Media Naranja
    url(r'^(?P<username>[a-zA-Z0-9-]+)/(?P<election_slug>[a-zA-Z0-9-]+)/medianaranja$', 'candidator.elections.views.medianaranja1',name='medianaranja1'),

    # Candidate detail view
    url(r'^(?P<username>[-\w]+)/(?P<election_slug>[-\w]+)/(?P<slug>[-\w]+)$', CandidateDetailView.as_view(), name='candidate_detail'),


)
