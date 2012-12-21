from django.test import TestCase
from django.template import Template, Context
from django.conf import settings

class SettingsVariablesInTemplate(TestCase):
	def setUp(self):
		pass

	def test_it_provides_uservoice_template_tag(self):
		settings.USERVOICE_CLIENT_KEY = "A KEY"
		template = Template('{% load settingsvars_tags %}{% uservoice_client_key %}')
		self.assertEqual(template.render(Context({})), "A KEY")