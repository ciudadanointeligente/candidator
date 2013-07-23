# -*- coding: utf-8 -*-
from tastypie.resources import ModelResource
from elections.models import Election, Category, Question, Answer, Candidate, PersonalData,\
                            PersonalDataCandidate, Link, Background, BackgroundCandidate, BackgroundCategory
from tastypie.authentication import ApiKeyAuthentication
from tastypie import fields

class ElectionV2Resource(ModelResource):
    candidates = fields.ToManyField('candidator.elections.api_v2.CandidateV2Resource', 'candidate_set', null=True)
    categories = fields.ToManyField('candidator.elections.api_v2.CategoryV2Resource', 'category_set', null=True)
    background_categories = fields.ToManyField('candidator.elections.api_v2.BackgroundCategoryV2Resource', 'backgroundcategory_set', null=True)
    personal_data = fields.ToManyField('candidator.elections.api_v2.PersonalDataV2Resource', 'personaldata_set', null=True)
    
    class Meta:
        queryset = Election.objects.all()
        resource_name = 'election'
        authentication = ApiKeyAuthentication()

    def authorized_read_list(self, object_list, bundle):
        return object_list.filter(owner=bundle.request.user)

class PersonalDataV2Resource(ModelResource):
    class Meta:
        queryset = PersonalData.objects.all()
        resource_name = 'personal_data'

class LinkV2Resource(ModelResource):
    class Meta:
        queryset = Link.objects.all()

class BackgroundV2Resource(ModelResource):
    class Meta:
        queryset = Background.objects.all()
        resource_name = 'background'

class PersonalDataCandidateV2Resource(ModelResource):
    candidate = fields.ToOneField('candidator.elections.api_v2.CandidateV2Resource','candidate')
    personal_data = fields.ToOneField('candidator.elections.api_v2.PersonalDataV2Resource','personal_data')

    class Meta:
        resource_name = 'personal_data_candidate'
        queryset = PersonalDataCandidate.objects.all()
        authentication = ApiKeyAuthentication()

class BackgroundsCandidateV2Resource(ModelResource):
    class Meta:
        resource_name = 'backgrounds_candidate'
        queryset = BackgroundCandidate.objects.all()

class CandidateV2Resource(ModelResource):
    # personal_data = fields.ManyToManyField(PersonalDataV2Resource, 'personal_data', null=True, full=True)
    links = fields.ToManyField(LinkV2Resource, 'link_set', full=True)
    personal_data_candidate = fields.ToManyField('candidator.elections.api_v2.PersonalDataCandidateV2Resource','personaldatacandidate_set', null=True)
    backgrounds_candidate = fields.ToManyField('candidator.elections.api_v2.BackgroundsCandidateV2Resource','backgroundcandidate_set', null=True)

    class Meta:
        queryset = Candidate.objects.all()
        resource_name = 'candidate'
        authentication = ApiKeyAuthentication()

class AnswerV2Resource(ModelResource):
    candidates = fields.ToManyField(CandidateV2Resource, 'candidate_set', null=True)

    class Meta:
        queryset = Answer.objects.all()
        resource_name = 'answer'
        authentication = ApiKeyAuthentication()

class QuestionV2Resource(ModelResource):
    answers = fields.ToManyField(AnswerV2Resource, 'answer_set', null=True)

    class Meta:
        queryset = Question.objects.all()
        resource_name = 'question'
        authentication = ApiKeyAuthentication()

class CategoryV2Resource(ModelResource):
    questions = fields.ToManyField(QuestionV2Resource, 'question_set', null=True)

    class Meta:
        queryset = Category.objects.all()
        resource_name = 'category'
        authentication = ApiKeyAuthentication()

class BackgroundCategoryV2Resource(ModelResource):
    background = fields.ToManyField('candidator.elections.api_v2.BackgroundV2Resource', 'background_set', null=True)

    class Meta:
        queryset = BackgroundCategory.objects.all()
        resource_name = 'background_category'
        authentication = ApiKeyAuthentication()