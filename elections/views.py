# Create your views here.
from django.http import HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DetailView
from django.utils import simplejson as json
from django.template.context import RequestContext
from django.contrib.auth.models import User

from models import Election, Candidate, Answer, PersonalInformation, Link, Category, Question
from forms import CategoryForm, ElectionForm


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
        return reverse('candidate_create', kwargs={'slug': self.object.slug})

    def form_valid(self, form):
        self.object = form.save(commit=False)
        # validate same slug for user
        if self.model.objects.filter(owner=self.request.user, slug=self.object.slug).count() > 0:
            return self.form_invalid(form)
        self.object.owner = self.request.user
        self.object.save()
        return redirect(self.get_success_url())


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


@login_required
@require_http_methods(['GET','POST'])
def create_election(request, my_user):
    if request.POST:
        form = ElectionForm(request.POST)    
        if form.is_valid():
            election_name = request.POST.get('name', None)
            election_description = request.POST.get('description', None)
            election_slug = request.POST.get('slug', None)               
            election_logo = request.POST.get('file_image', None)
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

def success_create_election(request):
    return render_to_response('elections/success_create_election.html')

def medianaranja1(request, my_user, election_slug):

    if request.method == "POST":
        importances = request.POST["importance"]
        id_answers = request.POST['question']
        #answer_importance = [ (answer[id], importances[id]) for id in answers.keys()]


        election = Election.objects.get(slug=election_slug, owner=my_user)
        candidates = election.candidate_set.all()
        categories = election.category_set.all()

        candidate_category = {}
        for candidate in candidates:
            candidate_category[candidate]={}
            for category in categories:
                candidate_category[candidate][category]=0

        for id in id_answers:
            category = answer.question.category
            candidates_same_answer = candidates.filter(answers__pk=id)

        #TODO: finish him


        return HttpResponse(answer_importance)
    else:
        u = User.objects.filter(username=my_user)
        if len(u) == 0:
            raise Http404
        e = Election.objects.filter(owner=u[0],slug=election_slug)
        if len(e) == 0:
            raise Http404
        return render_to_response('medianaranja1.html', {'election': e[0], 'categories': e[0].category_set}, context_instance = RequestContext(request))


def medianaranja2(request):
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
