from django.conf.urls.defaults import patterns, url
from django.views.generic import DetailView, ListView, TemplateView, CreateView
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required
from elections.views.answer_views import AnswerCreateAjaxView

from models import Election
from views.election_views import ElectionUpdateDataView
from views.candidate_views import CandidateUpdatePhotoView
from views import associate_answer_to_candidate, ElectionCreateView,\
                  ElectionUpdateView, ElectionDetailView, CandidateDetailView,\
                  CandidateCreateView, CandidateUpdateView, CategoryCreateView,\
                  CandidateCreateAjaxView, CategoryUpdateView, PersonalDataCreateView,\
                  BackgroundCategoryCreateView, BackgroundCreateView, QuestionCreateView,\
                  AnswerCreateView, personal_data_candidate_create, background_candidate_create,\
                  CandidateDataUpdateView, async_delete_candidate, async_create_background, \
                  async_delete_background, async_delete_background_category, \
                  PrePersonalDataView, AnswerDeleteAjaxView, ElectionLogoUpdateView, \
                  ElectionShareView, ElectionRedirectView, HomeTemplateView, CompareView, \
                  ElectionAboutView, ElectionStyleUpdateView, EmbededTemplateView, \
                  UserElectionsView, TogglePublishView


urlpatterns = patterns('',
    



    #frontend embed
    # Election detail view embeded
    url(r'^(?P<username>[-\w]+)/(?P<slug>[-\w]+)/embeded/?$', ElectionDetailView.as_view(template_name="elections/embeded/election_detail_profiles.html"), name='election_detail_embeded'),
    # Election candidates profiles
    url(r'^(?P<username>[-\w]+)/(?P<slug>[-\w]+)/profiles/embeded/?$', ElectionDetailView.as_view(template_name='elections/embeded/election_detail_profiles.html'), name='election_detail_profiles_embeded'),
    # Media Naranja
    url(r'^(?P<username>[a-zA-Z0-9-]+)/(?P<election_slug>[a-zA-Z0-9-]+)/medianaranja/embeded/?$', 'candidator.elections.views.medianaranja1_embed',name='medianaranja1_embeded'),

    # Election compare view
    url(r'^(?P<username>[-\w]+)/(?P<slug>[-\w]+)/compare/embeded/?$', CompareView.as_view(template_name='elections/embeded/election_compare.html'), name='election_compare_embeded'),

    # Election compare view with both candidates (and considering one category)
    url(r'^(?P<username>[-\w]+)/(?P<slug>[-\w]+)/compare/(?P<first_candidate_slug>[-\w]+)/(?P<second_candidate_slug>[-\w]+)/(?P<category_slug>[-\w]+)/embeded/?$', CompareView.as_view(template_name='elections/embeded/election_compare.html'), name='election_compare_two_candidates_embeded'),

    # Election compare view with both candidates (and NO category)
    url(r'^(?P<username>[-\w]+)/(?P<slug>[-\w]+)/compare/(?P<first_candidate_slug>[-\w]+)/(?P<second_candidate_slug>[-\w]+)/embeded/?$', CompareView.as_view(template_name='elections/embeded/election_compare.html'), name='election_compare_two_candidates_and_no_category_embeded'),

    # Election compare view with 1 candidate
    url(r'^(?P<username>[-\w]+)/(?P<slug>[-\w]+)/compare/(?P<first_candidate_slug>[-\w]+)/embeded?$', CompareView.as_view(template_name='elections/embeded/election_compare.html'), name='election_compare_one_candidate_embeded'),
     # Election description
    url(r'^(?P<username>[-\w]+)/(?P<slug>[-\w]+)/about/embeded?$', ElectionAboutView.as_view(template_name="elections/embeded/about.html"), name='election_about_embeded'),

    #frontend
    # Election candidates profiles





    url(r'^(?P<username>[-\w]+)/(?P<slug>[-\w]+)/profiles/?$', ElectionDetailView.as_view(template_name='elections/election_detail_profiles.html'), name='election_detail_profiles'),

    # Election compare view
    url(r'^(?P<username>[-\w]+)/(?P<slug>[-\w]+)/compare/?$', CompareView.as_view(template_name='elections/election_compare.html'), name='election_compare'),

    # Election compare view with both candidates (and considering one category)
    url(r'^(?P<username>[-\w]+)/(?P<slug>[-\w]+)/compare/(?P<first_candidate_slug>[-\w]+)/(?P<second_candidate_slug>[-\w]+)/(?P<category_slug>[-\w]+)/?$', CompareView.as_view(template_name='elections/election_compare.html'), name='election_compare_two_candidates'),

    # Election compare view with both candidates (and NO category)
    url(r'^(?P<username>[-\w]+)/(?P<slug>[-\w]+)/compare/(?P<first_candidate_slug>[-\w]+)/(?P<second_candidate_slug>[-\w]+)/?$', CompareView.as_view(template_name='elections/election_compare.html'), name='election_compare_two_candidates_and_no_category'),

    # Election compare view with 1 candidate
    url(r'^(?P<username>[-\w]+)/(?P<slug>[-\w]+)/compare/(?P<first_candidate_slug>[-\w]+)/?$', CompareView.as_view(template_name='elections/election_compare.html'), name='election_compare_one_candidate'),

    # Asynchronous call for compare view
    url(r'^(?P<username>[-\w]+)/(?P<slug>[-\w]+)/compare-async/(?P<candidate_slug>[-\w]+)/?$', 'candidator.elections.views.election_compare_asynchronous_call', name='election_compare_asynchronous_call'),

    # Election description
    url(r'^(?P<username>[-\w]+)/(?P<slug>[-\w]+)/about/?$', ElectionAboutView.as_view(), name='election_about'),
    # Election detail view
    url(r'^(?P<username>[-\w]+)/(?P<slug>[-\w]+)/$', ElectionDetailView.as_view(template_name='elections/election_detail_profiles.html'), name='election_detail'),

    # Root: login_required (por ahora pues no se ha definido un index)
    url(r'^$', HomeTemplateView.as_view(), name="home"),
    #Election redirects to my elections if I have at least one election or to create
    url(r'^election_redirect/$', login_required(ElectionRedirectView.as_view()), name='election_redirect'),
    # My Elections
    url(r'^my_election_list/$', login_required(TemplateView.as_view(template_name="elections/my_election_list.html")), name='my_election_list'),

    # Associate Candidate
    url(r'^(?P<election_slug>[-\w]+)/(?P<candidate_slug>[-\w]+)/associate_answers/',
            associate_answer_to_candidate,
            name='associate_answer_candidate'),

    # Create Answer Ajax
    url(r'answer_create/(?P<question_pk>\d+).json', AnswerCreateAjaxView.as_view(), name='answer_create_ajax'),
    
    #Delete Answer Ajax
    url(r'answer_delete/(?P<pk>\d+)', AnswerDeleteAjaxView.as_view(), \
        name='answer_delete_ajax'),


    # Create Link Ajax
    url(r'^(?P<candidate_pk>\d+)/create_link', 'candidator.elections.views.async_create_link', name='link_create_ajax'),

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

    # Election style update view
    url(r'^election/(?P<slug>[-\w]+)/update_style/?$', ElectionStyleUpdateView.as_view(), name='update_custom_style'),

    # Election share view
    url(r'^election/(?P<slug>[-\w]+)/share/?$', ElectionShareView.as_view(template_name='elections/updating/share.html'), name='share_my_election'),

    # Election detail view admin
    url(r'^(?P<username>[-\w]+)/(?P<slug>[-\w]+)/gracias$', ElectionDetailView.as_view(template_name='elections/wizard/thanks_for_using_us.html'), name='election_detail_admin'),

    url(r'^election/(?P<slug>[-\w]+)/questions/?', ElectionUpdateDataView.as_view(), name='election_update_data'),
    
    url(r'^election/(?P<pk>\d+)/update_election_photo', ElectionLogoUpdateView.as_view(), name="update_election_photo"),

    # Toggle publish election
    url(r'^elections/toggle_publish/(?P<pk>[-\d]+)/?$', TogglePublishView.as_view() , name = 'toggle_publish' ),

    # Media Naranja
    url(r'^(?P<username>[a-zA-Z0-9-]+)/(?P<election_slug>[a-zA-Z0-9-]+)/medianaranja$', 'candidator.elections.views.medianaranja1',name='medianaranja1'),
    




    # Update candidate view
    url(r'^(?P<election_slug>[-\w]+)/candidate/(?P<slug>[-\w]+)/update/?$', CandidateUpdateView.as_view(), name='candidate_update'),

    url(r'^election/update/candidate/(?P<pk>\d+)/photo/$', CandidateUpdatePhotoView.as_view(), name='update_candidate_photo'),

    # Create candidate view
    url(r'^(?P<election_slug>[-\w]+)/candidate/create/?$', CandidateCreateView.as_view(template_name='elections/wizard/step_two.html'),name='candidate_create'),

    # Create candidate view not in wizard
    url(r'^(?P<election_slug>[-\w]+)/candidate/create_alone/?$', CandidateCreateView.as_view(template_name='elections/updating/candidates.html'), name='candidate_create_alone'),

    # Create candidate using next button
    url(r'^(?P<election_slug>[-\w]+)/candidate/save_candidate/?$', CandidateCreateAjaxView.as_view(), name='async_create_candidate'),

    # List Candidates in json
    url(r'^(?P<username>[a-zA-Z0-9-]+)/(?P<election_slug>[a-zA-Z0-9-]+)/candidate_list.json/?$', 'candidator.elections.views.candidate_views.get_candidate_list_as_json', name='candidate_list_json'),

    # Delete candidate view in wizzard
    url(r'^candidate/async_delete/?$', 'candidator.elections.views.async_delete_candidate' , name='async_delete_candidate'),

    # Candidate data Update (PersonalData and Background)
    url(r'^(?P<election_slug>[-\w]+)/candidate/(?P<slug>[-\w]+)/data_update/?$', CandidateDataUpdateView.as_view(template_name="elections/updating/answers.html"), name='candidate_data_update'),

    # Multiple candidate data Update (answering questions for several candidates)
    url(r'^(?P<election_slug>[-\w]+)/multiple_candidate_data_update/?$', CandidateDataUpdateView.as_view(template_name="elections/updating/answers.html"), name='multiple_candidate_data_update'),

    # Multiple candidate data Update (answering questions for several candidates) but this is just the first time ritght after the wizard
    url(r'^(?P<election_slug>[-\w]+)/multiple_candidate_data_update_first_time/?$', CandidateDataUpdateView.as_view(template_name="elections/updating/answers.html", first_time=True), name='multiple_candidate_data_update_first_time'),

    # Pre-Create PersonalData
    url(r'^(?P<election_slug>[-\w]+)/pre_personaldata/?$', login_required(PrePersonalDataView.as_view(template_name="elections/wizard/step_two_point_five.html")), name='pre_personaldata'),

    # Create PersonalData
    url(r'^(?P<election_slug>[-\w]+)/personal_data/create/?$', PersonalDataCreateView.as_view(), name='personal_data_create'),

    # Create PersonalData Ajax
    url(r'^(?P<election_pk>[-\w]+)/personal_data/async_create/?$', 'candidator.elections.views.async_create_personal_data', name='async_create_personal_data'),

    # Delete personalData view in wizzard
    url(r'^(?P<personal_data_pk>[-\d]+)/personal_data/async_delete/?$', 'candidator.elections.views.async_delete_personal_data', name='async_delete_personal_data'),

    # Create PersonalDataCandidate
    url(r'^(?P<candidate_pk>[0-9]+)/(?P<personal_data_pk>[0-9]+)/personal_data_associate' , 'candidator.elections.views.personal_data_candidate_create', name='personal_data_candidate_create'),

    # Create BackgroundCategory
    url(r'^(?P<election_slug>[-\w]+)/background_category/create/?$', BackgroundCategoryCreateView.as_view(), name='background_category_create'),

    # Create BackgroundCategory Ajax
    url(r'^(?P<election_pk>[-\w]+)/background_category/async_create/?$', 'candidator.elections.views.async_create_background_category', name='async_create_background_category'),

     # Delete BackgroundCategory view in wizzard
    url(r'^(?P<category_pk>[-\d]+)/background_category/async_delete/?$', 'candidator.elections.views.async_delete_background_category' , name='async_delete_background_category'),

    # Create Background
    url(r'^(?P<background_category_pk>[0-9]+)/background/create/?$', BackgroundCreateView.as_view(), name='background_create'),

    # Create Background Ajax
    url(r'^(?P<background_category_pk>[0-9]+)/background/async_create/?$', 'candidator.elections.views.async_create_background', name='async_create_background'),

    # Delete background view in wizzard
    url(r'^(?P<background_pk>[-\d]+)/background/async_delete/?$', 'candidator.elections.views.async_delete_background' , name='async_delete_background'),

    # Create Category Ajax
    url(r'^(?P<election_pk>[-\w]+)/category/async_create/?$', 'candidator.elections.views.async_create_category', name='async_create_category'),

    # Delete category view in wizzard
    url(r'^(?P<category_pk>[0-9]+)/category/async_delete/?$', 'candidator.elections.views.async_delete_category' , name='async_delete_category'),

    # Create BackgroundCandidate
    url(r'^(?P<candidate_pk>[0-9]+)/(?P<background_pk>[0-9]+)/background_associate' , background_candidate_create, name='background_candidate_create'),

    # Delete question view in wizzard
    url(r'^(?P<question_pk>[0-9]+)/question/async_delete/?$', 'candidator.elections.views.async_delete_question' , name='async_delete_question'),

    # Create question view in wizzard
    url(r'^(?P<category_pk>[0-9]+)/question/async_create/?$', 'candidator.elections.views.async_create_question' , name='async_create_question'),

    # Delete link ajax
    url(r'^(?P<link_pk>[-\d]+)/link/async_delete/?$', 'candidator.elections.views.async_delete_link' , name='async_delete_link'),

    

    # Candidate detail view
    url(r'^(?P<username>[-\w]+)/(?P<election_slug>[-\w]+)/(?P<slug>[-\w]+)$', CandidateDetailView.as_view(), name='candidate_detail'),
    #embeded

    # Candidate detail view
    url(r'^(?P<username>[-\w]+)/(?P<election_slug>[-\w]+)/(?P<slug>[-\w]+)/embeded/?$', CandidateDetailView.as_view(template_name="elections/embeded/candidate_detail.html"), name='candidate_detail_embeded'),





    # Solo para efectos de prueba del embeded
    url(r'^prueba_embeded$', EmbededTemplateView.as_view(), name="prueba_embeded"),

    #Municipales 2012

    url(r'^municipales2012/?$', TemplateView.as_view(template_name="municipales2012.html"), name="municipales2012"),


    # Election detail view
    url(r'^(?P<username>[-\w]+)/?$', UserElectionsView.as_view(), name='user_elections'),


)
