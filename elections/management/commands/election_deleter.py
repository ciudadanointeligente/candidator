from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from elections.models import Election, Candidate, PersonalData, Category, Question, Answer, BackgroundCategory,\
							 Background, Link, BackgroundCandidate

class Command(BaseCommand):
	args = '<username>'
	def handle(self, *args, **options):
		username = args[0]
		user = User.objects.get(username=username)

		elections = Election.objects.filter(owner=user)
		for election in elections:
			candidates = Candidate.objects.filter(election=election)
			for candidate in candidates:
				personal_datas = candidate.personal_data.all()
				for personal_data in personal_datas:
					personal_data.delete()

				backgrounds = candidate.background.all()
				for background in backgrounds:
					background.delete()

			election.delete()