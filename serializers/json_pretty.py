# serializers/json_pretty.py
"""
Add the line to settings.py::

    SERIALIZATION_MODULES = {'json-pretty': 'serializers.json_pretty'}

And call dumpdata as follows::

    ./manage.py dumpdata --format=json-pretty <app_name>

"""

import codecs
from django.utils import simplejson
from django.core.serializers.json import Serializer as JSONSerializer
from django.core.serializers.json import Deserializer
from django.core.serializers.json import DjangoJSONEncoder

class Serializer(JSONSerializer):
    def end_serialization(self):
        stream = codecs.getwriter('utf8')(self.stream)
        simplejson.dump(self.objects, stream, cls=DjangoJSONEncoder,
                        ensure_ascii=False, **self.options)
