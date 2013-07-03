# -*- coding: utf-8 -*-
from tastypie.resources import ModelResource
from elections.models import Election, Category
from tastypie.authentication import ApiKeyAuthentication

class ElectionV2Resource(ModelResource):
    class Meta:
        queryset = Election.objects.all()
        resource_name = 'election'
        authentication = ApiKeyAuthentication()

    def authorized_read_list(self, object_list, bundle):
        return object_list.filter(owner=bundle.request.user)


class CategoryV2Resource(ModelResource):
    class Meta:
        queryset = Category.objects.all()
        resource_name = 'category'

