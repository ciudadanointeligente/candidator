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
from elections.forms import QuestionForm

# Import models
from elections.models import Category, Question, Election


# Question Views
class QuestionCreateView(CreateView):
    model = Question
    form_class = QuestionForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.election = get_object_or_404(Election, slug=kwargs['election_slug'], owner=request.user)
        return super(QuestionCreateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(QuestionCreateView, self).get_context_data(**kwargs)
        context['election'] = self.election
        return context

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(QuestionCreateView, self).get_form_kwargs(*args, **kwargs)
        kwargs['election'] = self.election
        return kwargs

    def get_success_url(self):
        return reverse('question_create', kwargs={'election_slug': self.object.category.election.slug})

    def form_invalid(self, form):
        print "zxcv"

    def form_valid(self, form):
        print "asd"
        return super(QuestionCreateView, self).form_valid(form)
    #     self.object = form.save(commit=False)
    #     election = get_object_or_404(Election, election=self.kwargs['election_slug'], owner=self.request.user)
    #     self.object.election = election
    #     self.object.save()
    #     return redirect(self.get_success_url())