# myapp/api.py
from tastypie.authentication import ApiKeyAuthentication
from tastypie.resources import ModelResource
from elections.models import Election, Candidate, Category, Question
from tastypie import fields

class CandidateResource(ModelResource):
	class Meta:
		queryset = Candidate.objects.all()
		resource_name = 'candidate'
		authentication = ApiKeyAuthentication()

	def obj_create(self, bundle, request=None, **kwargs):
		return super(CandidateResource, self).obj_create(bundle, request, user=request.user)

	def apply_authorization_limits(self, request, object_list):
		return object_list.filter(election__owner=request.user)

class QuestionResource(ModelResource):
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
	candidates = fields.ToManyField(CandidateResource, 'candidate_set', null=True, full=True)
	categories = fields.ToManyField(CategoryResource, 'category_set', full=True)

	class Meta:
		queryset = Election.objects.all()
		resource_name = 'election'
		
		excludes = ['custom_style']
		authentication = ApiKeyAuthentication()

	def obj_create(self, bundle, request=None, **kwargs):
		return super(ElectionResource, self).obj_create(bundle, request, user=request.user)

	def apply_authorization_limits(self, request, object_list):
		return object_list.filter(owner=request.user)



