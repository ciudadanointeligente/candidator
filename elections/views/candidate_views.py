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
from django.views.generic import CreateView, DetailView, UpdateView

# Import forms
from elections.forms import CandidateForm, CandidateUpdateForm, CandidateLinkFormset, CandidatePersonalInformationFormset

# Import models
from elections.models import Election, Candidate


# Candidate views
class CandidateDetailView(DetailView):
    model = Candidate

    def get_context_data(self, **kwargs):
        context = super(CandidateDetailView, self).get_context_data(**kwargs)
        context['election'] = self.object.election
        return context

    def get_queryset(self):
        if self.kwargs.has_key('username') and self.kwargs.has_key('election_slug') and self.kwargs.has_key('slug'):
            return self.model.objects.filter(election__owner__username=self.kwargs['username'],
                                             election__slug=self.kwargs['election_slug'],
                                             slug=self.kwargs['slug'])

        return super(CandidateDetailView, self).get_queryset()


class CandidateUpdateView(UpdateView):
    model = Candidate
    form_class = CandidateUpdateForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(CandidateUpdateView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        if self.kwargs.has_key('election_slug') and self.kwargs.has_key('slug'):
            return self.model.objects.filter(election__slug=self.kwargs['election_slug'],
                                                  slug=self.kwargs['slug'],
                                                  election__owner=self.request.user)

        return super(CandidateUpdateView, self).get_queryset()

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
        if self.request.POST:
            context['link_formset'] = CandidateLinkFormset(self.request.POST, prefix='link')
            context['personal_information_formset'] = CandidatePersonalInformationFormset(self.request.POST)
        else:
            context['personal_information_formset'] = CandidatePersonalInformationFormset()
            context['link_formset'] = CandidateLinkFormset(prefix='link')
        return context

    def get_success_url(self):
        return reverse('candidate_create', kwargs={'election_slug': self.object.election.slug})

    def form_valid(self, form):
        context = self.get_context_data()
        personal_information_formset = context['personal_information_formset']
        link_formset = context['link_formset']

        if personal_information_formset.is_valid() and link_formset.is_valid():
            self.object = form.save(commit=False)
            election = Election.objects.get(owner = self.request.user, slug=self.kwargs['election_slug'])
            self.object.election = election

            try:
                self.object.full_clean()
                self.object.save()
                for f in personal_information_formset:
                   personal_information = f.save(commit=False)
                   personal_information.candidate = self.object
                   personal_information.save()

                for f in link_formset:
                   link = f.save(commit=False)
                   link.candidate = self.object
                   link.save()

            except ValidationError:
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