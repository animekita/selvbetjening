from django.conf.urls import *

from tastypie.api import Api

from api import AttendeeResource

v1_api = Api(api_name='v1')
v1_api.register(AttendeeResource())

urlpatterns = patterns('',
    (r'^', include(v1_api.urls)),
)