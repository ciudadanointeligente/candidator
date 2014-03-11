from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.template import Template, Context

from elections.models import Report
from elections.forms import ReportForm


class ReportModelTest(TestCase):
    def test_create(self):
        user, created = User.objects.get_or_create(username='asd')
        report = Report.objects.create(content_object=user, reason='reason lorem ipsum')
        self.assertEquals(report.content_object, user)
        self.assertEquals(report.reason, 'reason lorem ipsum')

    def test_create_with_owner(self):
        user, created = User.objects.get_or_create(username='asd')
        report = Report.objects.create(content_object=user, reason='reason lorem ipsum', owner=user)
        self.assertEquals(report.content_object, user)
        self.assertEquals(report.reason, 'reason lorem ipsum')
        self.assertEquals(report.owner, user)


class ReportCreateViewTest(TestCase):
    '''
    '''
    def test_get_create_report(self):
        user = User.objects.create_user(username='foo', password='bar', email='foo@bar.com')
        content_type = ContentType.objects.get_for_model(User)
        url = reverse('report', kwargs={'object_id': user.pk, 'content_type': content_type.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('report_object' in response.context)
        self.assertTrue(isinstance(response.context['report_object'], User))
        self.assertEquals(response.context['report_object'], user)
        self.assertTrue('form' in response.context)
        self.assertTrue(isinstance(response.context['form'], ReportForm))
        self.assertTrue('reason' in response.context['form'].fields)

    def test_post_create_report(self):
        user = User.objects.create_user(username='foo', password='bar', email='foo@bar.com')
        content_type = ContentType.objects.get_for_model(User)
        url = reverse('report', kwargs={'object_id': user.pk, 'content_type': content_type.pk})
        response = self.client.post(url, {'reason': 'lorem ipsum dolor sit amet'}, follow=True)
        self.assertEqual(response.status_code, 200)
        report = Report.objects.get(pk=1)
        self.assertEquals(report.reason, 'lorem ipsum dolor sit amet')
    
    def test_get_create_report_without_content_type(self):
        user = User.objects.create_user(username='foo', password='bar', email='foo@bar.com')
        content_type = ContentType.objects.get_for_model(User)
        url = reverse('report', kwargs={'object_id': user.pk, 'content_type': 1000})
        response = self.client.post(url, params={'reason': 'lorem ipsum dolor sit amet'}, follow=True)
        self.assertEqual(response.status_code, 404)


class ReportTemplatetagTest(TestCase):
    def test_get_url_for(self):
        user = User.objects.create_user(username='foo', password='bar', email='foo@bar.com')
        content_type = ContentType.objects.get_for_model(User)
        result = Template(
            '{% load report_tags %}'
            '{% report_url user %}'
        ).render(Context({
            'user': user
        }))
        self.assertEquals(result, reverse('report', kwargs={'object_id': user.pk, 'content_type': content_type.pk}))

class ReportURLTest(TestCase):
    
    def test_create(self):
        url = reverse('report', kwargs={'object_id': 1, 'content_type': 3})
        self.assertEquals(url, '/report/3/1')
