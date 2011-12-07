from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType


class Report(models.Model):
    owner = models.ForeignKey('auth.User', null=True)
    reason = models.TextField(max_length=512)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    @models.permalink
    def get_absolute_url(self):
        return ('report_detail', None, {'pk': self.pk})
