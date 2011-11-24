# Create your views here.

from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.forms import formsets
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.template.context import RequestContext
from django.utils import simplejson as json
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, DetailView

from forms import CandidateForm, CategoryForm, ElectionForm, CandidatePersonalInformationForm, CandidatePersonalInformationFormset
from models import Election, Candidate, Answer, PersonalInformation, Link, Category, Question


# Candidate views
class CandidateDetailView(DetailView):
    model = Candidate

    def get_queryset(self):
        if self.kwargs.has_key('username') and self.kwargs.has_key('election_slug') and self.kwargs.has_key('slug'):
            return self.model.objects.filter(election__owner__username=self.kwargs['username'],
                                             election__slug=self.kwargs['election_slug'],
                                             slug=self.kwargs['slug'])

        return super(CandidateDetailView, self).get_queryset()


# Election views
class ElectionDetailView(DetailView):
    model = Election

    def get_queryset(self):
        if self.kwargs.has_key('username') and self.kwargs.has_key('slug'):
            return self.model.objects.filter(owner__username=self.kwargs['username'],
                                             slug=self.kwargs['slug'])
        return super(ElectionDetailView, self).get_queryset()

class CandidateCreateView(CreateView):
    model = Candidate
    form_class = CandidateForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(CandidateCreateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CandidateCreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = CandidatePersonalInformationFormset(self.request.POST)
        else:
            context['formset'] = CandidatePersonalInformationFormset()
        return context

    def get_success_url(self):
        return reverse('candidate_create', kwargs={'slug': self.object.election.slug})

    def form_valid(self, form):
        self.object = form.save(commit=False)
        election = Election.objects.get(owner = self.request.user, slug=self.kwargs['slug'])
        self.object.election = election
        try:
            self.object.full_clean()
        except ValidationError:
            from django.forms.util import ErrorList
            form._errors["slug"] = ErrorList([u"Ya tienes un candidato con ese slug."])
            return super(CandidateCreateView, self).form_invalid(form)

        return super(CandidateCreateView, self).form_valid(form)

class ElectionCreateView(CreateView):
    model = Election
    form_class = ElectionForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ElectionCreateView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('candidate_create', kwargs={'slug': self.object.slug})

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


class CategoryCreateView(CreateView):
    model = Category
    form_class = CategoryForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(CategoryCreateView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('election_detail', kwargs={'slug': self.object.election.slug, 'username': self.request.user.username})

    def form_valid(self, form):
        self.object = form.save(commit=False)
        election = Election.objects.get(slug=self.kwargs['election_slug'], owner=self.request.user)
        self.object.election = election

        try:
            self.object.full_clean()
        except ValidationError:
            from django.forms.util import ErrorList
            form._errors["slug"] = ErrorList([u"Ya tienes una categoria con ese slug."])
            return super(CategoryCreateView, self).form_invalid(form)

        return super(CategoryCreateView, self).form_valid(form)

@login_required
@require_http_methods(['GET', 'POST'])
def associate_answer_to_candidate(request, slug, election_slug):
    election = get_object_or_404(Election, slug=election_slug, owner=request.user)
    candidate = get_object_or_404(Candidate, slug=slug, election=election)
    if request.POST:
        answer_id = request.POST.get('answer', None)
        answer = get_object_or_404(Answer, pk=answer_id, question__category__election=election)
        candidate.associate_answer(answer)
        return HttpResponse(json.dumps({'answer': answer.pk}),
                            content_type='application/json')
    return render_to_response(\
            'elections/associate_answer.html', {'candidate': candidate, 'categories': election.category_set},
            context_instance=RequestContext(request))

'''
@login_required
@require_http_methods(['GET','POST'])
def create_election(request, my_user):
    if request.POST:
        form = ElectionForm(request.POST, request.FILES)
        if form.is_valid():
            election_name = request.POST.get('name', None)
            election_description = request.POST.get('description', None)
            election_slug = request.POST.get('slug', None)
            election_logo = request.FILES['logo']
            election = Election(name = election_name, slug = election_slug, owner = request.user, description = election_description, logo = election_logo)
            #this code is because form doesnt validate owner
            bad_election = Election.objects.filter(slug = election_slug, owner = request.user)

            if len(bad_election) > 0:
                return render_to_response('elections/create_election.html', {'form': form, 'error_duplicated_slug': True}, context_instance = RequestContext(request))
            election.save()
            return redirect('/elections/success_create_election/')
        else:
            return render_to_response('elections/create_election.html', {'form': form}, context_instance = RequestContext(request))
    return render_to_response('elections/create_election.html', {'form': ElectionForm}, context_instance = RequestContext(request))
'''

def success_create_election(request):
    return render_to_response('elections/success_create_election.html')

def medianaranja1(request, my_user, election_slug):

    if request.method == "POST":
        #importances = request.POST["importance"]
        #id_answers = request.POST['question']
        #answer_importance = [ (answer[id], importances[id]) for id in answers.keys()]

        user_list = User.objects.filter(username=my_user)
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
        #    answers.append(Answer.objects.get(id=int(request.POST['question-'+str(i)])))
            ans_id = int(request.POST['question-'+str(i)])
            answers.append(Answer.objects.filter(id=ans_id))
            importances.append(int(request.POST['importance-'+str(i)]))
        # print answers
        # print importances

        return medianaranja2(request, answers, importances, candidates)
        #TODO: modificar medianaranja2 + calculo de puntaje

    else:
        u = User.objects.filter(username=my_user)
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
                empty_questions.append((counter,y,y.get_answers()))
                counter += 1
            send_to_template.append((x,empty_questions))

        return render_to_response('medianaranja1.html', {'stt':send_to_template,'election': e[0], 'categories': e[0].category_set}, context_instance = RequestContext(request))


def medianaranja2(request, my_answers, importances, candidates):
    max_score = 0
    winner = ''
    score_all_candidates_by_categories = []
    for candidate in candidates:
        #print candidate.get_score(my_answers, importances)
        #score = (sum(candidate.get_score(my_answers, importances)) / sum(importances)) * 100.0
        #TODO score all candidates by categories --> get sum(importances) by categories
        score = sum(candidate.get_score(my_answers, importances))
        if score > max_score:
            max_score = score
            winner = candidate
    print (winner, (max_score*100.0 / sum(importances)))
    return render_to_response('medianaranja2.html', {}, context_instance = RequestContext(request))

@login_required
@require_http_methods(['GET', 'POST'])
def add_category(request, election_slug):
    election = get_object_or_404(Election, slug=election_slug, owner=request.user)

    if request.method == 'GET':
        form = CategoryForm()
        return render_to_response('add_category.html', {'form':form}, context_instance=RequestContext(request))
    elif request.POST:
        form2 = CategoryForm(request.POST)
        if form2.is_valid():
            category = form2.save(commit=False)
            category.election = election
            category.save()
            form = CategoryForm()
            return render_to_response('add_category.html', {'form':form}, context_instance=RequestContext(request))
        else:
            return render_to_response('add_category.html', {'form':form2}, context_instance=RequestContext(request))

        raise Http404
    else:
        raise Http404
