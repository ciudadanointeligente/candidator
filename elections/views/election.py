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

from elections.forms import ElectionForm, ElectionUpdateForm
from elections.models import Election


class ElectionUpdateView(UpdateView):
    model = Election
    form_class = ElectionUpdateForm

    def get_success_url(self):
        return reverse('election_update', kwargs={'slug': self.object.slug})

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        election = get_object_or_404(Election, slug=kwargs['slug'], owner=request.user)
        return super(ElectionUpdateView, self).dispatch(request, *args, **kwargs)


# Election views
class ElectionDetailView(DetailView):
    model = Election

    def get_queryset(self):
        if self.kwargs.has_key('username') and self.kwargs.has_key('slug'):
            return self.model.objects.filter(owner__username=self.kwargs['username'],
                                             slug=self.kwargs['slug'])
        return super(ElectionDetailView, self).get_queryset()


class ElectionCreateView(CreateView):
    model = Election
    form_class = ElectionForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ElectionCreateView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('candidate_create', kwargs={'election_slug': self.object.slug})

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        try:
            self.object.full_clean()
        except ValidationError:
            from django.forms.util import ErrorList
            form._errors["slug"] = ErrorList([u"Ya tienes una eleccion con ese slug."])
            return super(ElectionCreateView, self).form_invalid(form)

        return super(ElectionCreateView, self).form_valid(form)
