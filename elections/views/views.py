# Create your views here.

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

from elections.forms import CandidateForm, CandidateUpdateForm, CategoryForm, ElectionForm,\
                  CandidatePersonalInformationForm, CandidatePersonalInformationFormset,\
                  CandidateLinkFormset, ElectionUpdateForm, CategoryUpdateForm,\
                  PersonalDataForm, BackgroundCategoryForm, BackgroundForm, QuestionForm
from elections.models import Election, Candidate, Answer, PersonalInformation,\
                   Link, Category, Question, PersonalData,\
                   BackgroundCategory, Background


# Candidate views
class CandidateDetailView(DetailView):
    model = Candidate

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
        return super(CandidateUpdateView, self).get_queryset().filter(election__slug=self.kwargs['election_slug'], election__owner=self.request.user)

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


class CategoryCreateView(CreateView):
    model = Category
    form_class = CategoryForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(CategoryCreateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CategoryCreateView, self).get_context_data(**kwargs)
        context['election'] = get_object_or_404(Election, slug=self.kwargs['election_slug'], owner=self.request.user)
        return context

    def get_success_url(self):
        return reverse('category_create', kwargs={'election_slug': self.object.election.slug})

    def form_valid(self, form):
        self.object = form.save(commit=False)
        election = get_object_or_404(Election, slug=self.kwargs['election_slug'], owner=self.request.user)
        self.object.election = election

        try:
            self.object.full_clean()
        except ValidationError:
            from django.forms.util import ErrorList
            form._errors["slug"] = ErrorList([u"Ya tienes una categoria con ese slug."])
            return super(CategoryCreateView, self).form_invalid(form)

        return super(CategoryCreateView, self).form_valid(form)

class CategoryUpdateView(UpdateView):
    model = Category
    form_class = CategoryUpdateForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(CategoryUpdateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CategoryUpdateView, self).get_context_data(**kwargs)
        context['election'] = get_object_or_404(Election, slug=self.kwargs['election_slug'], owner=self.request.user)
        return context

    def get_success_url(self):
        return reverse('election_detail', kwargs={'slug': self.object.election.slug, 'username': self.request.user.username})

    def get_queryset(self):
        if self.kwargs.has_key('election_slug') and self.kwargs.has_key('slug'):
            return self.model.objects.filter(election__slug=self.kwargs['election_slug'],
                                             slug=self.kwargs['slug'],
                                             election__owner=self.request.user)
        return super(ElectionDetailView, self).get_queryset()

    def form_valid(self, form):
        self.object = form.save(commit=False)
        election = get_object_or_404(Election, slug=self.kwargs['election_slug'], owner=self.request.user)
        self.object.election = election
        return super(CategoryUpdateView, self).form_valid(form)


class PersonalDataCreateView(CreateView):
    model = PersonalData
    form_class = PersonalDataForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(PersonalDataCreateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PersonalDataCreateView, self).get_context_data(**kwargs)
        context['election'] = get_object_or_404(Election, slug=self.kwargs['election_slug'], owner=self.request.user)
        return context

    def get_success_url(self):
        return reverse('personal_data_create', kwargs={'election_slug': self.kwargs['election_slug']})

    def form_valid(self, form):
        self.object = form.save(commit=False)
        election = get_object_or_404(Election, slug=self.kwargs['election_slug'], owner=self.request.user)
        self.object.election = election
        return super(PersonalDataCreateView, self).form_valid(form)


class BackgroundCategoryCreateView(CreateView):
    model = BackgroundCategory
    form_class = BackgroundCategoryForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(BackgroundCategoryCreateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(BackgroundCategoryCreateView, self).get_context_data(**kwargs)
        context['election'] = get_object_or_404(Election, slug=self.kwargs['election_slug'], owner=self.request.user)
        return context

    def get_success_url(self):
        return reverse('background_category_create', kwargs={'election_slug': self.object.election.slug})

    def form_valid(self, form):
        self.object = form.save(commit=False)
        election = get_object_or_404(Election, slug=self.kwargs['election_slug'], owner=self.request.user)
        self.object.election = election
        return super(BackgroundCategoryCreateView, self).form_valid(form)


class BackgroundCreateView(CreateView):
    model = Background
    form_class = BackgroundForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(BackgroundCreateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(BackgroundCreateView, self).get_context_data(**kwargs)
        context['background_category'] = get_object_or_404(BackgroundCategory, pk=self.kwargs['background_category_pk'], election__owner=self.request.user)
        return context

    def get_success_url(self):
        return reverse('background_category_create', kwargs={'election_slug': self.object.category.election.slug})

    def form_valid(self, form):
        self.object = form.save(commit=False)
        background_category = get_object_or_404(BackgroundCategory, pk=self.kwargs['background_category_pk'], election__owner=self.request.user)
        self.object.category = background_category
        return super(BackgroundCreateView, self).form_valid(form)


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



@login_required
@require_http_methods(['GET', 'POST'])
def associate_answer_to_candidate(request, candidate_slug, election_slug):
    election = get_object_or_404(Election, slug=election_slug, owner=request.user)
    candidate = get_object_or_404(Candidate, slug=candidate_slug, election=election)
    if request.POST:
        answer_id = request.POST.get('answer', None)
        answer = get_object_or_404(Answer, pk=answer_id, question__category__election=election)
        candidate.associate_answer(answer)
        return HttpResponse(json.dumps({'answer': answer.pk}),
                            content_type='application/json')
    return render_to_response(\
            'elections/associate_answer.html', {'candidate': candidate, 'categories': election.category_set},
            context_instance=RequestContext(request))

def post_medianaranja1(request, username, election_slug):
    user_list = User.objects.filter(username=username)
    if len(user_list) == 0:
        raise Http404

    election = Election.objects.get(slug=election_slug, owner=User.objects.get(username=user_list[0]))

    candidates = election.candidate_set.all()
    categories = election.category_set.all()

    number_of_questions = 0
    for c in categories:
        number_of_questions += len(c.get_questions())

    importances = []
    answers = []

    for i in range(number_of_questions):
        ans_id = int(request.POST['question-'+str(i)])
        answers.append(Answer.objects.filter(id=ans_id))
        importances.append(int(request.POST['importance-'+str(i)]))

    return medianaranja2(request, answers, importances, candidates, categories)

def get_medianaranja1(request, username, election_slug):
    u = User.objects.filter(username=username)
    if len(u) == 0:
        raise Http404
    e = Election.objects.filter(owner=u[0],slug=election_slug)
    if len(e) == 0:
        raise Http404

    send_to_template = []
    counter = 0
    for x in e[0].category_set.all():
        empty_questions = []
        list_questions = x.get_questions()
        for i in range(len(list_questions)):
            y = list_questions[i]
            empty_questions.append((counter,y,y.answer_set.all()))
            counter += 1
        send_to_template.append((x,empty_questions))

    return render_to_response('medianaranja1.html', {'stt':send_to_template,'election': e[0], 'categories': e[0].category_set}, context_instance = RequestContext(request))


def medianaranja1(request, username, election_slug):

    if request.method == "POST":
        return post_medianaranja1(request, username, election_slug)

    else:
        return get_medianaranja1(request, username, election_slug)

def medianaranja2(request, my_answers, importances, candidates, categories):

    scores_and_candidates = []

    for candidate in candidates:
        score = candidate.get_score(my_answers, importances)
        global_score = score[0]
        category_scores = score[1]
        scores_and_candidates.append([global_score,category_scores,candidate])
    scores_and_candidates.sort()
    scores_and_candidates.reverse()

    winner = scores_and_candidates[0]
    other_candidates = scores_and_candidates[1:]
    return render_to_response('medianaranja2.html', {'categories':categories,'winner':winner,'others':other_candidates}, context_instance = RequestContext(request))



