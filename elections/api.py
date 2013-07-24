# myapp/api.py
from tastypie.authentication import ApiKeyAuthentication
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.resources import ModelResource
from elections.models import Election, Candidate, Category, Question, Answer, \
							PersonalData, PersonalDataCandidate, Link, Background, BackgroundCandidate
from tastypie import fields
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse

class PersonalDataResource(ModelResource):
	class Meta:
		queryset = PersonalData.objects.all()

class LinkResource(ModelResource):
	class Meta:
		queryset = Link.objects.all()

class BackgroundResource(ModelResource):
	class Meta:
		queryset = Background.objects.all()

class CandidateResource(ModelResource):
	personal_data = fields.ManyToManyField(PersonalDataResource, 'personal_data', null=True, full=True)
	links = fields.ToManyField(LinkResource, 'link_set', full=True)
	background = fields.ManyToManyField(BackgroundResource, 'background', full=True)

	class Meta:
		queryset = Candidate.objects.all()
		resource_name = 'candidate'
		authentication = ApiKeyAuthentication()

	def authorized_read_list(self, object_list, bundle):
		return object_list.filter(election__owner=bundle.request.user)

	def dehydrate(self, bundle):
		candidate = bundle.obj
		categories = bundle.obj.election.category_set.all()
		bundle.data["categories"] = []
		
		for category in categories:
			questions_array = []
			for question in category.question_set.all():
				answers = Answer.objects.filter(question=question).filter(candidate=candidate)
				the_answer = None
				if len(answers)==1:
					the_answer = {
						"id":answers[0].id,
						"caption":answers[0].caption
					}
				questions_array.append({
						"id": question.id,
						"answer": the_answer,
						"question": question.question
					})
			
			category_dict = {
				"id":category.id,
				"name":category.name,
				"questions":questions_array
			}

			bundle.data["categories"].append(category_dict)


		for pdata in bundle.data['personal_data']:
			personal_data_candidate = PersonalDataCandidate.objects.get(candidate=bundle.obj, personal_data=pdata.obj)
			pdata.data['value'] = personal_data_candidate.value
			del pdata.data['resource_uri']
		
		for data in bundle.data['background']:
			background_candidate = BackgroundCandidate.objects.get(candidate=bundle.obj, background=data.obj)
			data.data['value'] = background_candidate.value

		return bundle

class AnswerResource(ModelResource):
	class Meta:
		queryset = Answer.objects.all()
		resource_name = 'answer'

class QuestionResource(ModelResource):
	possible_answers = fields.ToManyField(AnswerResource, 'answer_set', null=True, full=True)
	class Meta:
		queryset= Question.objects.all()
		resource_name = 'question'
		authentication = ApiKeyAuthentication()

class CategoryResource(ModelResource):
	questions = fields.ToManyField(QuestionResource, 'question_set', null=True, full=True)
	class Meta:
		queryset = Category.objects.all()
		resource_name = 'category'
		authentication = ApiKeyAuthentication()

class ElectionResource(ModelResource):
	candidates = fields.ToManyField(CandidateResource, 'candidate_set', null=True, full=False)
	categories = fields.ToManyField(CategoryResource, 'category_set', full=True)


	class Meta:
		queryset = Election.objects.all()
		resource_name = 'election'
		filtering = {"slug": ALL_WITH_RELATIONS, "name": ALL_WITH_RELATIONS }
		
		excludes = ['custom_style']
		authentication = ApiKeyAuthentication()

	def authorized_read_list(self, object_list, bundle):
		return object_list.filter(owner=bundle.request.user)

	def dehydrate(self, bundle):
		candidates_list = []
		for i, candidate in enumerate(bundle.obj.candidate_set.all()):
			candidates_list.append({'name':candidate.name, 'resource_uri':bundle.data['candidates'][i], 'id':candidate.id, 'image':candidate.photo})
		bundle.data['candidates'] = candidates_list
		current_site = Site.objects.get_current()
		bundle.data['url'] = "http://"+current_site.domain+bundle.obj.get_absolute_url()
		embeded_url = reverse('election_detail_embeded',kwargs={'username': bundle.obj.owner.username,'slug': bundle.obj.slug})
		bundle.data['embedded_url'] = "http://"+current_site.domain+embeded_url
		return bundle