from django.conf.urls import *

from tastypie.api import Api

from api import AttendeeResource, UserResource, EventResource, SelectionResource,\
    OptionGroupResource, OptionResource, SubOptionResource, PaymentResource, InvoiceResource,\
    AttendeeCommentResource

v1_api = Api(api_name='v1')
v1_api.register(EventResource())
v1_api.register(UserResource())
v1_api.register(AttendeeResource())
v1_api.register(SelectionResource())
v1_api.register(OptionGroupResource())
v1_api.register(OptionResource())
v1_api.register(SubOptionResource())
v1_api.register(PaymentResource())
v1_api.register(InvoiceResource())
v1_api.register(AttendeeCommentResource())

urlpatterns = patterns('',
    (r'^', include(v1_api.urls)),
)