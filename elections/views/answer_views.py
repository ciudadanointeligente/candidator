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
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, DetailView, UpdateView
from django.views.generic.edit import BaseDeleteView

# Import forms
from elections.forms import AnswerForm

# Import models
from elections.models import Answer, Question


class AnswerCreateAjaxView(CreateView):
    model = Answer
    form_class = AnswerForm

    def dispatch(self, request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseBadRequest()
        self.question = get_object_or_404(Question, pk=kwargs['question_pk'])
        if self.question.category.election.owner != request.user:
            return HttpResponseForbidden()
        return super(AnswerCreateAjaxView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.question = self.question
        self.object.save()
        return HttpResponse(content=simplejson.dumps(
                {'pk': self.object.pk, 'caption': self.object.caption, 'question': self.question.pk}),
                content_type='application/json')

    def form_invalid(self, form):
        return HttpResponse(content=simplejson.dumps(
            {'error': form.errors}),
            content_type='application/json')


# Answer View
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



class AnswerDeleteAjaxView(BaseDeleteView):
    model = Answer
    pk_url_kwarg = 'pk'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AnswerDeleteAjaxView, self).dispatch(request, *args, \
                **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.question.category.election.owner != request.user:
            raise Http404
        self.object.delete()
        json_dictionary = {"result":"OK"}
        return HttpResponse(json.dumps(json_dictionary),content_type='application/json')


