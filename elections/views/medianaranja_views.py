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
from django.views.decorators.csrf import csrf_exempt

from elections.models import Election, Candidate, Answer, Category, Question, Visitor, VisitorAnswer, VisitorScore, CategoryScore

# MediaNaranja Views
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


def strip_elements_from_dictionary(dictionary, election):
    candidates = election.candidate_set.all()
    categories = election.category_set.all()

    number_of_questions = 0
    for c in categories:
        number_of_questions += len(c.question_set.all())

    importances = []
    answers = []
    questions = []

    for i in range(number_of_questions):
        if 'question-'+str(i) in dictionary:
            ans_id = int(dictionary['question-'+str(i)])
        else:
            ans_id = -1
        question_id = int(dictionary['question-id-'+str(i)])
        answers.append(Answer.objects.filter(id=ans_id))
        importances.append(int(dictionary['importance-'+str(i)]))
        questions.append(Question.objects.get(id=question_id))

    return {
        'answers': answers, 
        'importances' : importances, 
        'questions' : questions, 
        'candidates' : candidates, 
        'categories' : categories
    }

def post_medianaranja1(request, username, election_slug):
    user_list = User.objects.filter(username=username)
    if user_list.count() == 0:
        raise Http404

    election = Election.objects.get(slug=election_slug, owner=User.objects.get(username=user_list[0]))

    elements = strip_elements_from_dictionary(request.POST, election)

    return medianaranja2(elements["answers"], elements['importances'], elements['questions'], elements['candidates'], elements['categories'], election)

def get_medianaranja1(request, username, election_slug):
    election = get_object_or_404(Election, owner__username=username, slug=election_slug)

    send_to_template = []
    counter = 0
    check = False
    for x in election.category_set.all():
        empty_questions = []
        list_questions = x.question_set.all()
        for i in range(len(list_questions)):
            y = list_questions[i]
            empty_questions.append((counter,y,y.answer_set.all()))
            counter += 1
        send_to_template.append((x,empty_questions))
        for tupla in send_to_template:
            if len(tupla[1]) > 0:
                check = True
                break

    return {'stt':send_to_template, 'check': check, 'election': election}

def medianaranja1(request, username, election_slug):

    if request.method == "POST":
        context = post_medianaranja1(request, username, election_slug)
        return render_to_response('medianaranja2.html', context, context_instance = RequestContext(request))

    else:
        context = get_medianaranja1(request, username, election_slug)
        return render_to_response('medianaranja1.html', context, context_instance = RequestContext(request))

@csrf_exempt
def medianaranja1_embed(request, username, election_slug):
    if request.method == "POST":
        context = post_medianaranja1(request, username, election_slug)
        return render_to_response('elections/embeded/medianaranja2.html', context, context_instance = RequestContext(request))
    else:
        context = get_medianaranja1(request, username, election_slug)
        return render_to_response('elections/embeded/medianaranja1.html', context, context_instance = RequestContext(request))

def medianaranja2(my_answers, importances, questions, candidates, categories, election):
    election_url=reverse("election_detail",kwargs={'username': election.owner.username, 'slug':election.slug})
    visitor = Visitor(election=election, election_url=election_url)
    visitor.save()
    #save answers for latter analysis:
    for i, importance in enumerate(importances):
        if my_answers[i]:
            visitoranswer = VisitorAnswer(visitor=visitor,answer=my_answers[i][0], answer_importance=importance)
        else:
            visitoranswer = VisitorAnswer(visitor=visitor,answer_text="",question_text=questions[i].question,\
                question_category_text=questions[i].category.name, answer_importance=importance)
        visitoranswer.save()

    scores_and_candidates = []
    for candidate in candidates:
        score = candidate.get_score(my_answers, importances)
        global_score = score[0]
        category_scores = score[1]
        visitor_score = VisitorScore.objects.create(visitor=visitor, candidate_name=candidate.name,score=global_score)
        for i,category_score in enumerate(category_scores):
            categoryscore = CategoryScore.objects.create(visitor_score=visitor_score,category_score=category_score, category_name=categories[i])

        scores_and_candidates.append([global_score,category_scores,candidate])
    scores_and_candidates.sort()
    scores_and_candidates.reverse()

    winner = scores_and_candidates[0]
    other_candidates = scores_and_candidates[1:]
    


    

    context = {'election':election, 'categories':categories,'winner':winner,'others':other_candidates}
    return context
