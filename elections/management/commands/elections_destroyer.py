# coding= utf-8
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from elections.models import Election

class ElectionDestructor(object):
	def __init__(self,username):
		self.user = User.objects.get(username=username)
		self.elections = Election.objects.filter(owner=self.user)

	def process(self):
		for election in self.elections:
			election.personaldata_set.all().delete()
			election.backgroundcategory_set.all().delete()
			election.category_set.all().delete()
		self.elections.delete()

class Command(BaseCommand):
	args = '<username>'
	def handle(self, *args, **options):
		username = args[0]
		destructor = ElectionDestructor(username)
		destructor.process()