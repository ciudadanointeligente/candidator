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
