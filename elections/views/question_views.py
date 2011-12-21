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
from elections.models import Category, Question


# Question Views
class QuestionCreateView(CreateView):
    model = Question
    form_class = QuestionForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(QuestionCreateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(QuestionCreateView, self).get_context_data(**kwargs)
        context['category'] = get_object_or_404(Category, pk=self.kwargs['category_pk'], election__owner=self.request.user)
        return context

    def get_success_url(self):
        return reverse('category_create', kwargs={'election_slug': self.object.category.election.slug})

    def form_valid(self, form):
        self.object = form.save(commit=False)
        category = get_object_or_404(Category, pk=self.kwargs['category_pk'], election__owner=self.request.user)
        self.object.category = category
        return super(QuestionCreateView, self).form_valid(form)