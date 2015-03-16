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

@register.simple_tag
def socialmedia_custom_message(election, candidate, category_score):
    str_template = election.custom_success_socialmedia
    if election.custom_success_socialmedia == '':
        str_template = 'Mi media naranja politica en {{ election_name }} es {{ candidate_name }}.'

    t = template.Template (str_template)
    c = template.Context({ 'election_name': election.name, 'candidate_name': candidate.name, 'category_score': "{0:.0f}%".format(category_score) })

    return t.render(c)
    