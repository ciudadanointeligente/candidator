# Create your views here.
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.utils import simplejson as json

from models import Election, Candidate, Answer


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
