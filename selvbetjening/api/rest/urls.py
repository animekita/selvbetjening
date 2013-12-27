
from django.conf.urls import url, patterns, include

from tastypie.api import Api
from selvbetjening.api.rest.models import AuthenticatedUserResource

v1_api = Api(api_name='v1')
v1_api.register(AuthenticatedUserResource())

urlpatterns = patterns('',
    url(r'^', include(v1_api.urls)),
)