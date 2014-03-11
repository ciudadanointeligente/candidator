#encoding=UTF-8
from django import template
from django.utils.translation import ugettext as _
from elections.models import PersonalDataCandidate, BackgroundCandidate

register = template.Library()


@register.simple_tag
def value_for_candidate_and_personal_data(candidate, personal_data):
    '''
    Returns the answer for the given candidate and question pair.

    >> {% answer_for_candidate_and_question candidate question %}
    "answer"
    '''

    try:
        return PersonalDataCandidate.objects.get(candidate=candidate, personal_data=personal_data).value
    except PersonalDataCandidate.DoesNotExist:
        pass
    return ''

@register.simple_tag
def value_for_candidate_and_background(candidate, background):
    '''
    Returns the answer for the given candidate and question pair.

    >> {% answer_for_candidate_and_question candidate question %}
    "answer"
    '''

    try:
        return BackgroundCandidate.objects.get(candidate=candidate, background=background).value
    except BackgroundCandidate.DoesNotExist:
        pass
    return ''

# @register.simple_tag
# def candidate_photo(candidate):
#     '''
#     @deprecated
#     return the url for candidate photo or empty string
#     '''
#     try:
#         return candidate.photo.url
#     except ValueError, e:
#         pass
#     return ''

