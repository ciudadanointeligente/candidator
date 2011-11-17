# Create your views here.
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.utils import simplejson as json
from django.template.context import RequestContext
from django.contrib.auth.models import User

<<<<<<< HEAD
from models import Election, Candidate, Answer, PersonalInformation, Link, Category, Question, ElectionForm
from forms import CategoryForm



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
            form.save()
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

    if request.GET:
        form = CategoryForm()
        return render_to_response('add_category.html', {'form':form},\
                context_instance=RequestContext(request))
    elif request.POST:
        raise Http404
