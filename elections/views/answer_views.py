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

from elections.forms import AnswerForm
from elections.models import Answer, Question


class AnswerCreateView(CreateView):
    model = Answer
    form_class = AnswerForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AnswerCreateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(AnswerCreateView, self).get_context_data(**kwargs)
        context['question'] = get_object_or_404(Question, pk=self.kwargs['question_pk'], category__election__owner=self.request.user)
        return context

    def get_success_url(self):
        return reverse('category_create', kwargs={'election_slug': self.object.question.category.election.slug})

    def form_valid(self, form):
        self.object = form.save(commit=False)
        question = get_object_or_404(Question, pk=self.kwargs['question_pk'], category__election__owner=self.request.user)
        self.object.question = question
        return super(AnswerCreateView, self).form_valid(form)