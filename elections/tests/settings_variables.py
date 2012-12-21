from django.test import TestCase
from django.template import Template, Context
from django.conf import settings

class SettingsVariablesInTemplate(TestCase):
	def setUp(self):
		pass

	def test_it_provides_uservoice_template_tag(self):
		settings.USERVOICE_CLIENT_KEY = "USERVOICE KEY"
		template = Template('{% load settingsvars_tags %}{% uservoice_client_key %}')
		self.assertEqual(template.render(Context({})), "USERVOICE KEY")

	def test_it_provides_google_analytics_template_tag(self):
		settings.GOOGLE_ANALYTICS_ACCOUNT_ID = "GOOGLE ANALYTICS ACCOUNT ID"
		template = Template('{% load settingsvars_tags %}{% ga_account_id %}')
		self.assertEqual(template.render(Context({})), "GOOGLE ANALYTICS ACCOUNT ID")