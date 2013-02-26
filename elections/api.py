# myapp/api.py
from tastypie.authentication import ApiKeyAuthentication
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.resources import ModelResource
from elections.models import Election, Candidate, Category, Question, Answer, PersonalData, PersonalDataCandidate
from tastypie import fields

class PersonalDataResource(ModelResource):
	class Meta:
		queryset = PersonalData.objects.all()

class CandidateResource(ModelResource):
	personal_data = fields.ManyToManyField(PersonalDataResource, 'personal_data', null=True, full=True)
	class Meta:
		queryset = Candidate.objects.all()
		resource_name = 'candidate'
		authentication = ApiKeyAuthentication()

	def authorized_read_list(self, object_list, bundle):
		return object_list.filter(election__owner=bundle.request.user)

	def dehydrate(self, bundle):
		for pdata in bundle.data['personal_data']:
			personal_data_candidate = PersonalDataCandidate.objects.get(candidate=bundle.obj, personal_data=pdata.obj)
			pdata.data['value'] = personal_data_candidate.value
			del pdata.data['resource_uri']
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
			candidates_list.append({'name':candidate.name, 'resource_uri':bundle.data['candidates'][i]})
		bundle.data['candidates'] = candidates_list
		return bundle
