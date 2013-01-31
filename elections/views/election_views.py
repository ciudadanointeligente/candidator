from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.forms import formsets
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.template.context import RequestContext
from django.utils import simplejson as json
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, DetailView, UpdateView, ListView, TemplateView, RedirectView
from django.contrib.sites.models import Site
from django.views.decorators.http import require_POST


# Import forms
from elections.forms import ElectionForm, ElectionUpdateForm, PersonalDataForm,\
                            BackgroundCategoryForm, BackgroundForm, QuestionForm, \
                            CategoryForm, ElectionStyleUpdateForm

# Import models
from elections.forms.candidate_form import CandidateForm
from elections.forms.election_form import AnswerForm, ElectionLogoUpdateForm
from elections.models import Election, Candidate, Category

from django.conf import settings

# Election Views
class ElectionLogoUpdateView(UpdateView):
    model = Election
    form_class = ElectionLogoUpdateForm
    
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.election = get_object_or_404(Election, pk=kwargs['pk'], owner=request.user)
        return super(ElectionLogoUpdateView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(ElectionLogoUpdateView, self).get_form_kwargs()
        kwargs['election'] = self.object
        return kwargs
    
    def get_template_names(self):
        return 'elections/updating/election_logo_form.html'

    def get_success_url(self):
        url = reverse('election_update', kwargs={'slug': self.object.slug})
        return url

class ElectionStyleUpdateView(UpdateView):
    model = Election
    form_class = ElectionStyleUpdateForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.election = get_object_or_404(Election, slug=kwargs['slug'], owner=request.user)
        return super(ElectionStyleUpdateView, self).dispatch(request, *args, **kwargs)

    def get_template_names(self):
        return 'elections/updating/election_style_updating.html'

    def get_queryset(self):
        return super(ElectionStyleUpdateView, self).get_queryset().filter(owner=self.request.user)

    def get_success_url(self):
        url = reverse('update_custom_style', kwargs={'slug': self.object.slug})
        return url


class ElectionUpdateView(UpdateView):
    model = Election
    form_class = ElectionUpdateForm

    def get_template_names(self):
        return 'elections/updating/election_basic_information.html'

    def get_success_url(self):
        return reverse('election_update', kwargs={'slug': self.object.slug})

    def get_context_data(self, **kwargs):
        context = super(ElectionUpdateView, self).get_context_data(**kwargs)
        election = kwargs['form'].instance
        context['election_url'] = self.request.build_absolute_uri(election.get_absolute_url())
        new_candidate_form = CandidateForm()
        context['new_candidate_form'] = new_candidate_form
        return context

    def get_queryset(self):
        return super(ElectionUpdateView, self).get_queryset().filter(owner=self.request.user)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        election = get_object_or_404(Election, slug=kwargs['slug'], owner=request.user)
        return super(ElectionUpdateView, self).dispatch(request, *args, **kwargs)


# Election views
class ElectionDetailView(DetailView):
    model = Election

    def get_queryset(self):

        return super(ElectionDetailView, self).get_queryset().filter(owner__username=self.kwargs['username']).filter(published=True)

class ElectionShareView(DetailView):
    model = Election
    def get_queryset(self):
        return super(ElectionShareView, self).get_queryset().filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
            self.object.published=True
            self.object.save()
            context = super(ElectionShareView, self).get_context_data(**kwargs)
            return context
    # def get_queryset(self):
    #     return super(ElectionDetailView, self).get_queryset().filter(owner__username=self.kwargs['username']).filter(published=True)



class ElectionCreateView(CreateView):
    model = Election
    form_class = ElectionForm
    
    def get_template_names(self):
        return ['elections/wizard/step_one.html']

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ElectionCreateView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('candidate_create', kwargs={'election_slug': self.object.slug})

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.set_slug()
        self.object.full_clean()

        return super(ElectionCreateView, self).form_valid(form)

# Election views
class CompareView(DetailView):
    model = Election

    def get_queryset(self):
        return super(CompareView, self).get_queryset().filter(owner__username=self.kwargs['username']).filter(published=True)


    def get_context_data(self, **kwargs):
        context = super(CompareView, self).get_context_data(**kwargs)
        username = self.kwargs['username']
        slug = self.kwargs['slug']
        #Seleccionar esto del get_queryset
        #con algo como self.object
        election = get_object_or_404(Election, owner__username=username, slug=slug)
        context["election"] = election

        if('first_candidate_slug' in self.kwargs):

            first_candidate_slug = self.kwargs['first_candidate_slug']

            first_candidate = get_object_or_404(Candidate, election=election, slug=first_candidate_slug)
            context['first_candidate'] = first_candidate
            if('second_candidate_slug' in self.kwargs):
                second_candidate_slug = self.kwargs['second_candidate_slug']
                second_candidate = get_object_or_404(Candidate, election=election, slug=second_candidate_slug)
                context['second_candidate'] = second_candidate

                if first_candidate == second_candidate:
                    raise Http404
                if 'category_slug' in self.kwargs:
                    category_slug = self.kwargs['category_slug']
                    selected_category = get_object_or_404(Category, election=election, slug=category_slug)
                    first_candidate_answers = first_candidate.get_all_answers_by_category(selected_category)
                    second_candidate_answers = second_candidate.get_all_answers_by_category(selected_category)
                    answers = first_candidate.get_answers_two_candidates(second_candidate,selected_category)
                    context['selected_category'] = selected_category
                    context['answers'] = answers
                else:
                    return context

            else:
                return context
        else:
            return context
        facebook_link = 'http'
        site = Site.objects.get_current()
        if self.request.is_secure(): facebook_link += 's'
        facebook_link += '://' + site.domain + '/' + username + '/' + slug + '/compare/'
        facebook_link += min(first_candidate_slug,second_candidate_slug) + '/' + max(first_candidate_slug,second_candidate_slug)+ '/' + category_slug
        
        
        
        context['facebook_link'] = facebook_link
        return context

@require_POST
def election_compare_asynchronous_call(request, username, slug, candidate_slug):
    election = get_object_or_404(Election, slug=slug, owner__username=username)
    candidate = get_object_or_404(Candidate, slug=candidate_slug, election=election)
    personal_data = candidate.get_personal_data
    try:
        photo_route = str(candidate.photo.url)
    except :
        photo_route = 'media/photos/dummy.jpg'
    json_dictionary = {"personal_data":personal_data,"photo_route":photo_route}
    return HttpResponse(json.dumps(json_dictionary),content_type='application/json')




# Election views
class ElectionAboutView(DetailView):
    model = Election
    template_name = "elections/election_about.html"
    def get_template_names(self):
        return [self.template_name]

    def get_queryset(self):

        return super(ElectionAboutView, self).get_queryset().filter(owner__username=self.kwargs['username']).filter(published=True)


class PrePersonalDataView(TemplateView):

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.election = get_object_or_404(Election, slug=kwargs['election_slug'], owner=request.user)
        return super(PrePersonalDataView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PrePersonalDataView, self).get_context_data(**kwargs)
        context['election'] = self.election
        return context

class ElectionUpdateDataView(DetailView):
    model = Election
    def get_template_names(self):
        return ['elections/updating/questions.html']

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ElectionUpdateDataView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ElectionUpdateDataView, self).get_context_data(**kwargs)
        context['personaldata_form'] = PersonalDataForm()
        context['backgroundcategory_form'] = BackgroundCategoryForm()
        context['background_form'] = BackgroundForm()
        context['question_form'] = QuestionForm(election=self.object)
        context['category_form'] = CategoryForm()
        context['answer_form'] = AnswerForm()
        return context

    def get_queryset(self):
        return super(ElectionUpdateDataView, self).get_queryset().filter(owner=self.request.user)

class ElectionRedirectView(RedirectView):
    permanent = False

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ElectionRedirectView, self).dispatch(request, *args, **kwargs)

    def get_redirect_url(self, **kwargs):
        num_elections = self.request.user.election_set.count()
        if self.request.user.election_set.count() <= 0:
            return reverse('election_create')
        last_election = self.request.user.election_set.latest('pk')
        if last_election.candidate_set.count() <= 0:
            return reverse('election_detail_admin',
                           kwargs={'slug': last_election.slug, 'username': self.request.user.username})
        return reverse('candidate_data_update',
                       kwargs={'election_slug': last_election.slug, 'slug': last_election.candidate_set.all()[0].slug})


class HomeTemplateView(TemplateView):
    template_name = 'home.html'


    def get_context_data(self,**kwargs):
        last_five_elections = Election.objects.filter(published=True).order_by('-created_at')[:5]
        kwargs['last_elections'] = last_five_elections
        kwargs['highlighted_elections'] = Election.objects.filter(highlighted=True).filter(published=True).order_by('?')[:5]

        return kwargs

class UserElectionsView(TemplateView):
    template_name = 'elections/users_election_list.html'

    def get_context_data(self, **kwargs):
        user = get_object_or_404(User, username=kwargs['username'])
        user_elections = Election.objects.filter(published=True).filter(owner=user)
        context = super(UserElectionsView, self).get_context_data(**kwargs)
        context['elections'] = user_elections

        context['owner'] = user


        return context

##THIS IS ONLY FOR TESTING PORPOUSES

class EmbededTemplateView(TemplateView):
    template_name = 'prueba.html'

    def get_context_data(self, **kwargs):
        return {'embeded_test_web':settings.EMBEDED_TEST_WEB}

class TogglePublishView(UpdateView):
    model = Election
    http_method_names = ['post']

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            http_response = HttpResponse('Unauthorized', {}, {})
            http_response.status_code = 401
            return http_response
        return super(TogglePublishView, self).dispatch(request, *args, **kwargs)

    def get_template_names(self):
        return []

    def post(self, request, *args, **kwargs):
        election = self.get_object()
        if election.owner != request.user:
            http_response = HttpResponse('Forbidden', {}, {})
            http_response.status_code = 403
            return http_response
        election.published = not election.published
        election.save()
        response_data = {}
        response_data['published'] = election.published
        response_data['id'] = election.id
        return HttpResponse(json.dumps(response_data), content_type='application/json')