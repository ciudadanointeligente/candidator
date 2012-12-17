#encoding=UTF-8
from django import template
from django.utils.translation import ugettext as _
from elections.models import Answer

register = template.Library()


@register.simple_tag
def answer_for_candidate_and_question(candidate, question):
    '''
    Returns the answer for the given candidate and question pair.

    >> {% answer_for_candidate_and_question candidate question %}
    "answer"
    '''

    try:
        return question.answer_set.get(candidate=candidate).caption
    except Answer.DoesNotExist:
        pass
    return _(u"Aún no hay respuesta")
    
    
@register.simple_tag
def link_to_updating_this_election(user, election):
    from django.core.urlresolvers import reverse
    is_the_owner = not (user is None) and (election.owner.username == user.username)
    
    if is_the_owner:
        return '<span class="goedit"><a href="'+reverse('election_update',kwargs={"slug":election.slug})+'">'+_(u"Editar Elección")+'</a></span>'
    return ''
