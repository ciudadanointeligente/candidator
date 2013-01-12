from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.forms import formsets
from django.http import HttpResponse, Http404, HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.template.context import RequestContext
from django.utils import simplejson as json, simplejson
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, DetailView, UpdateView, ListView
from django.utils.translation import ugettext_lazy as _


# Import forms
from elections.forms import CandidateForm, CandidateUpdateForm, CandidateLinkForm, BackgroundCandidateForm, AnswerForm, PersonalDataCandidateForm, CandidatePhotoForm

# Import models
from elections.models import Election, Candidate, PersonalData, Link

# Import exceptions
from elections.exceptions import NoCandidateError

# Candidate views
class CandidateDetailView(DetailView):
    model = Candidate

    def get_context_data(self, **kwargs):
        context = super(CandidateDetailView, self).get_context_data(**kwargs)
        context['election'] = self.object.election
        return context

    def get_queryset(self):
        return self.model.objects.filter(election__owner__username=self.kwargs['username'],
                                         election__slug=self.kwargs['election_slug'],
                                         slug=self.kwargs['slug'])


class CandidateUpdateView(UpdateView):
    model = Candidate
    form_class = CandidateUpdateForm
    
    def get_template_names(self):
        return ['elections/wizard/step_two.html']
    
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(CandidateUpdateView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.model.objects.filter(election__slug=self.kwargs['election_slug'],
                                          slug=self.kwargs['slug'],
                                          election__owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(CandidateUpdateView, self).get_context_data(**kwargs)
        context['election'] = get_object_or_404(Election, slug=self.kwargs['election_slug'], owner=self.request.user)
        return context

    def get_success_url(self):
        return reverse('candidate_update', kwargs={'slug': self.kwargs['slug'], 'election_slug': self.object.election.slug})


class CandidateCreateView(CreateView):
    model = Candidate
    form_class = CandidateForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(CandidateCreateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CandidateCreateView, self).get_context_data(**kwargs)
        context['election'] = get_object_or_404(Election, slug=self.kwargs['election_slug'], owner=self.request.user)
        return context

    def get_success_url(self):
        url_to_updating_candidates = reverse('candidate_create_alone', kwargs={'election_slug': self.object.election.slug})
        if self.request.path_info == url_to_updating_candidates:
            return url_to_updating_candidates
        return reverse('candidate_create', kwargs={'election_slug': self.object.election.slug})

    def form_valid(self, form):
        self.object = form.save(commit=False)
        election = get_object_or_404(Election, slug=self.kwargs['election_slug'], owner=self.request.user)
        self.object.election = election
        try:
            self.object.full_clean()
            self.object.save()
        except ValidationError as e:
            from django.forms.util import ErrorList
            form._errors["nombre"] = ErrorList([u"Ya tienes un candidato con ese nombre."])
            return super(CandidateCreateView, self).form_invalid(form)
        return super(CandidateCreateView, self).form_valid(form)



class CandidateDataUpdateView(UpdateView):
    model = Candidate
    form_class = CandidateForm
    first_time = False
                
    @method_decorator(login_required)
    @method_decorator(require_GET)
    def dispatch(self, request, *args, **kwargs):
        try:
            return super(CandidateDataUpdateView, self).dispatch(request, *args, **kwargs)
        except NoCandidateError:
            return redirect("candidate_create_alone", election_slug=self.kwargs['election_slug'])


    def get_queryset(self):
        try:
            election = Election.objects.get(slug=self.kwargs['election_slug'],owner=self.request.user)
        except:
            return Election.objects.none()

        if 'slug' not in self.kwargs:
            candidates = election.candidate_set.all()
            if not candidates:
                raise NoCandidateError(_(u"There are no candidates"),[_(u"There are no candidates")])
            self.kwargs['slug'] = candidates[0].slug

        return self.model.objects.filter(election=election,
                                          slug=self.kwargs['slug'])



    def get_context_data(self, **kwargs):
        context = super(CandidateDataUpdateView, self).get_context_data(**kwargs)
        context['election'] = get_object_or_404(Election, slug=self.kwargs['election_slug'], owner=self.request.user)
        context['candidate_link_form'] = CandidateLinkForm()
        context['background_candidate_form'] = BackgroundCandidateForm()
        context['personal_data_candidate_form'] = PersonalDataCandidateForm()
        context['answer_form'] = AnswerForm()
        context['first_time'] = self.first_time
        return context


@login_required
@require_POST
def async_delete_candidate(request):
    candidate_pk = request.POST['candidate_pk']
    candidate = get_object_or_404(Candidate, pk=candidate_pk, election__owner=request.user)
    candidate.delete()
    json_dictionary = {"result":"OK"}
    return HttpResponse(json.dumps(json_dictionary),content_type='application/json')


@require_POST
def get_candidate_list_as_json(request,username,election_slug):
    election = get_object_or_404(Election, owner__username=username, slug=election_slug)
    candidates = election.candidate_set.all()
    result = []
    for candidate in candidates:
        result.append({'name' : candidate.name,'id' : candidate.id})
    return HttpResponse(json.dumps(result),content_type='application/json')

class CandidateCreateAjaxView(CreateView):
    model = Candidate
    form_class = CandidateForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseBadRequest()
        self.election = get_object_or_404(Election, owner=request.user, slug=kwargs['election_slug'])
        return super(CandidateCreateAjaxView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        election = get_object_or_404(Election, slug=self.kwargs['election_slug'], owner=self.request.user)
        self.object.election = election
        try:
            self.object.full_clean()
            self.object.save()
        except ValidationError as e:
            from django.forms.util import ErrorList
            form._errors["slug"] = ErrorList([u"Ya tienes un candidato con ese slug."])
            return HttpResponse(content=simplejson.dumps(
                {'error': form.errors}),
                content_type='application/json')

        self.object = form.save(commit=False)
        self.object.election = self.election
        self.object.save()
        json_dictionary = {"result": "OK"}
        return HttpResponse(json.dumps(json_dictionary),content_type='application/json')

    def form_invalid(self, form):
        return HttpResponse(content=simplejson.dumps({'error': form.errors}), content_type='application/json')

@login_required
@require_POST
def async_create_link(request, candidate_pk):
    link_name = request.POST.get('link_name', False)
    link_url = request.POST.get('link_url', False)
    election_slug = request.POST.get('election_slug', False)
    slug = request.POST.get('candidate_slug', False)
    cand_name = request.POST.get('candidate_name', False)
    election = get_object_or_404(Election, slug=election_slug, owner=request.user)
    candidate = get_object_or_404(Candidate, slug=slug, election=election, name=cand_name)
    link = Link(name = link_name, url= link_url, candidate = candidate)
    try:
        link.full_clean()
        link.save()
        json_dictionary = {"result": "OK", 'name':link_name, 'url':link.http_prefix, 'pk':link.pk}
    except ValidationError as e:
        json_dictionary = {"result":"NOK", "errors":e.message_dict}
    return HttpResponse(json.dumps(json_dictionary),content_type='application/json')

   

@login_required
@require_POST
def async_delete_link(request, link_pk):
    link = get_object_or_404(Link, pk = link_pk, candidate__election__owner = request.user)
    link.delete()
    json_dictionary = {"result":"OK"}
    return HttpResponse(json.dumps(json_dictionary),content_type='application/json')

class CandidateUpdatePhotoView(UpdateView):
    form_class = CandidatePhotoForm
    model = Candidate

    def get_template_names(self):
        return 'elections/candidate_photo_form.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if Candidate.objects.filter(pk=kwargs['pk'], election__owner=request.user).count() <= 0:
            return HttpResponseForbidden()
        return super(CandidateUpdatePhotoView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(CandidateUpdatePhotoView, self).get_form_kwargs()
        kwargs['candidate'] = self.object
        return kwargs

    def get_success_url(self):
        return reverse('candidate_data_update',
                       kwargs={'election_slug': self.object.election.slug, 'slug': self.object.slug})

