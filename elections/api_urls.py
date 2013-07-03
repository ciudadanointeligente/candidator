from django.conf.urls.defaults import *

from tastypie.api import Api
from elections.api import ElectionResource, CandidateResource
from elections.api_v2 import ElectionV2Resource, CategoryV2Resource

v1_api = Api(api_name='v1')
v1_api.register(ElectionResource())
v1_api.register(CandidateResource())

v2_api = Api(api_name='v2')
v2_api.register(ElectionV2Resource())
v2_api.register(CategoryV2Resource())

urlpatterns = patterns('',
    (r'^', include(v1_api.urls),),
    (r'^', include(v2_api.urls),),
)