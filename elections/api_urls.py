from django.conf.urls.defaults import *

from tastypie.api import Api
from elections.api import ElectionResource, CandidateResource

v1_api = Api(api_name='v1')
v1_api.register(ElectionResource())
v1_api.register(CandidateResource())

urlpatterns = patterns('',
	(
		r'^', include(v1_api.urls)),
	)