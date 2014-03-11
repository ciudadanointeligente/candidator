from django import template
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType

register = template.Library()


@register.simple_tag
def report_url(obj):
    '''
    Returns the url for reporting any object.

    >> {% report_url user %}
    "/report/1/2"
    '''
    content_type = ContentType.objects.get_for_model(type(obj))
    return reverse('report', kwargs={'object_id': obj.pk, 'content_type': content_type.pk})
