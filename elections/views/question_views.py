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
from django.views.decorators.http import require_http_methods, require_POST
from django.views.generic import CreateView, DetailView, UpdateView

# Import forms
from elections.forms import QuestionForm

# Import models
from elections.models import Category, Question, Election, Answer


# Question Views
class QuestionCreateView(CreateView):
    model = Question
    form_class = QuestionForm
    
    def get_template_names(self):
        return ['elections/wizard/step_five.html']

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


@login_required
@require_POST
def async_delete_question(request, question_pk):
    question = get_object_or_404(Question, pk = question_pk, category__election__owner = request.user)
    question.delete()
    json_dictionary = {"result":"OK"}
    return HttpResponse(json.dumps(json_dictionary),content_type='application/json')


@login_required
@require_http_methods(['POST'])
def async_create_question(request, category_pk):
    pass
    category = get_object_or_404(Category, pk=category_pk, election__owner=request.user)

    value = request.POST.get('value', None)
    question = Question(question=value, category=category)

    try:
        
        question.full_clean()
        question.save()
        return HttpResponse(json.dumps({"pk": question.pk, "question": question.question}),
                        content_type='application/json')
    except Exception as e:
        errors = {
            'error':e.message_dict
        }
        return HttpResponse(json.dumps(errors),
                        content_type='application/json')
        
    


# class QuestionCreateAjaxView(CreateView):
#     model = Question
#     form_class = QuestionForm

#     @method_decorator(login_required)
#     @method_decorator(require_POST)
#     def dispatch(self, request, *args, **kwargs):
#         if not request.is_ajax():
#             return HttpResponseBadRequest()
#         self.category = get_object_or_404(Category, pk=kwargs['category_pk'], election__owner=request.user)
#         if self.category.election.owner != request.user:
#             return HttpResponseForbidden()
#         return super(QuestionCreateAjaxView, self).dispatch(request, *args, **kwargs)

#     def form_valid(self, form):
#         self.object = form.save(commit=False)
#         self.object.category = self.category
#         self.object.save()
#         return HttpResponse(content=json.dumps({"pk": question.pk, "question": question.question}),
#                 content_type='application/json')

#     def form_invalid(self, form):

#         return HttpResponse(content=json.dumps(
#             {'error': form.errors}),
#             content_type='application/json')

#     def get_context_data(self, **kwargs):
#         context = super(QuestionCreateAjaxView, self).get_context_data(**kwargs)
#         context['election'] = self.category.election
#         return context

#     def get_form_kwargs(self, *args, **kwargs):
#         self.object = Question(question=self.request.POST['value'],category=self.category)
#         print(self.object.category)
#         kwargs = super(QuestionCreateAjaxView, self).get_form_kwargs(*args, **kwargs)
#         kwargs['election'] = self.category.election

        
#         return kwargs