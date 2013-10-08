# -*- coding: utf-8 -*-
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS, Resource
from elections.models import Election, Category, Question, Answer, Candidate, PersonalData,\
                            PersonalDataCandidate, Link, Background, BackgroundCandidate, BackgroundCategory,\
                            InformationSource
from tastypie.authentication import ApiKeyAuthentication
from tastypie import fields
from tastypie.serializers import Serializer

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
        authentication = ApiKeyAuthentication()

class LinkV2Resource(ModelResource):
    class Meta:
        queryset = Link.objects.all()
        resource_name = 'link'
        authentication = ApiKeyAuthentication()

class BackgroundV2Resource(ModelResource):
    background_category = fields.ToOneField('candidator.elections.api_v2.BackgroundCategoryV2Resource','category')

    class Meta:
        queryset = Background.objects.all()
        resource_name = 'background'
        authentication = ApiKeyAuthentication()

class PersonalDataCandidateV2Resource(ModelResource):
    candidate = fields.ToOneField('candidator.elections.api_v2.CandidateV2Resource','candidate')
    personal_data = fields.ToOneField('candidator.elections.api_v2.PersonalDataV2Resource','personal_data')

    class Meta:
        resource_name = 'personal_data_candidate'
        queryset = PersonalDataCandidate.objects.all()
        authentication = ApiKeyAuthentication()

class BackgroundsCandidateV2Resource(ModelResource):
    background = fields.ToOneField('candidator.elections.api_v2.BackgroundV2Resource','background')

    class Meta:
        resource_name = 'backgrounds_candidate'
        queryset = BackgroundCandidate.objects.all()

class CandidateV2Resource(ModelResource):
    # personal_data = fields.ManyToManyField(PersonalDataV2Resource, 'personal_data', null=True, full=True)
    links = fields.ToManyField(LinkV2Resource, 'link_set', null=True)
    personal_data_candidate = fields.ToManyField('candidator.elections.api_v2.PersonalDataCandidateV2Resource','personaldatacandidate_set', null=True)
    backgrounds_candidate = fields.ToManyField('candidator.elections.api_v2.BackgroundsCandidateV2Resource','backgroundcandidate_set', null=True)
    answers = fields.ToManyField('candidator.elections.api_v2.AnswerV2Resource','answers', null=True)

    class Meta:
        queryset = Candidate.objects.all()
        resource_name = 'candidate'
        authentication = ApiKeyAuthentication()
        filtering = {
            'id' : ALL
        }

class AnswerV2Resource(ModelResource):
    question = fields.ToOneField('candidator.elections.api_v2.QuestionV2Resource', 'question')
    candidates = fields.ToManyField(CandidateV2Resource, 'candidate_set', null=True)

    class Meta:
        queryset = Answer.objects.all()
        resource_name = 'answer'
        authentication = ApiKeyAuthentication()
        filtering = {
            'question' : ALL,
            'candidate' : ALL
        }

class QuestionV2Resource(ModelResource):
    category = fields.ToOneField('candidator.elections.api_v2.CategoryV2Resource', 'category', null=True)
    answers = fields.ToManyField(AnswerV2Resource, 'answer_set', null=True)
    information_sources = fields.ToManyField('candidator.elections.api_v2.InformationSourceResource', 'informationsource_set', null=True)

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

from candidator.elections.views import strip_elements_from_dictionary, medianaranja2

class MediaNaranjaResource(Resource):
    class Meta:
        resource_name = 'medianaranja'
        object_class = dict
        always_return_data = True
        serializer = Serializer(formats=['jsonp', 'json'])

    def obj_create(self,bundle,**kwargs):
        election = Election.objects.get(id=bundle.data["election-id"])

        elements = strip_elements_from_dictionary(bundle.data["data"],election)
        result = medianaranja2(elements["answers"], elements['importances'], elements['questions'], elements['candidates'], elements['categories'], election)
        bundle.obj = result
        bundle.data = result
        return bundle

    def detail_uri_kwargs(self, bundle):
        return {}

    def serialize(self, request, data, format, options=None):
        winner = data.data["winner"]
        others = data.data["others"]
        data.data["winner"] = {
                'global_score':winner[0], 
                'category_score':winner[1], 
                'candidate':winner[2].id
                }
        categories = data.data["categories"]
        counter = 0
        scores = []
        for score  in data.data["winner"]["category_score"]:
            category_dict = {
             "category":categories[counter].name,
             "score":score
            }
            scores.append(category_dict)
            counter += 1
        data.data["winner"]["category_score"] = scores

        others_counter = 0
        for other in others:
            others_dict = {
                'global_score':other[0], 
                'category_score':other[1], 
                'candidate':other[2].id
            }
            score_counter = 0
            scores = []
            for score in others_dict["category_score"]:
                category_dict = {
                 "category":categories[score_counter].name,
                 "score":score
                }
                scores.append(category_dict)

                score_counter += 1

            others_dict["category_score"] = scores



            data.data["others"][others_counter] = others_dict
            others_counter += 1

        serialized = super(MediaNaranjaResource, self).serialize(request, data, format, options)

        return serialized

class InformationSourceResource(ModelResource):
    candidate = fields.ToOneField('candidator.elections.api_v2.CandidateV2Resource','candidate')
    question = fields.ToOneField('candidator.elections.api_v2.QuestionV2Resource', 'question')


    class Meta:
        queryset = InformationSource.objects.all()
        resource_name = 'information_source'
        authentication = ApiKeyAuthentication()