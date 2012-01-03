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
from django.views.decorators.http import require_POST
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, DetailView, UpdateView

# Import forms
from elections.forms import CandidateForm, CandidateUpdateForm, CandidateLinkFormset

# Import models
from elections.models import Election, Candidate, PersonalData


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
            form._errors["slug"] = ErrorList([u"Ya tienes un candidato con ese slug."])
            return super(CandidateCreateView, self).form_invalid(form)
        return super(CandidateCreateView, self).form_valid(form)


@login_required
@require_http_methods(['GET'])
def candidate_data_update(request, election_slug, slug):
    election = get_object_or_404(Election, slug=election_slug, owner=request.user)
    candidate = get_object_or_404(Candidate, slug=slug, election=election)

    return render_to_response(\
            'elections/candidate_data_update.html',
            {'candidate': candidate, 'election': election},
            context_instance=RequestContext(request))


@login_required
@require_POST
def async_delete_candidate(request, candidate_pk):
    candidate = get_object_or_404(Candidate, pk=candidate_pk, election__owner=request.user)
    candidate.delete()
    json_dictionary = {"result":"OK"}
    return HttpResponse(json.dumps(json_dictionary),content_type='application/json')


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


#@login_required
#@require_POST
#def async_create_candidate(request, election_slug):
#    cand = request.POST.get('candidate', False)
#    election = get_object_or_404(Election, slug=election_slug, owner=request.user)
#    c = Candidate.objects.create(name = cand, election = election)
#    c.save()
#    json_dictionary = {"result": "OK"}
#    return HttpResponse(json.dumps(json_dictionary),content_type='application/json')
