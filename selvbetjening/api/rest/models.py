
from tastypie.authentication import Authentication
from tastypie.resources import ModelResource
from tastypie import fields

from provider.oauth2.models import AccessToken
from selvbetjening.core.events.models import Event, AttendState, Attend

from selvbetjening.core.members.models import SUser


class OAuth2Authentication(Authentication):

    def is_authenticated(self, request, **kwargs):

        access_key = request.REQUEST.get('access_key', None)

        if not access_key:
            auth_header_value = request.META.get('HTTP_AUTHORIZATION', None)
            if auth_header_value:
                access_key = auth_header_value.split(' ')[1]

        if not access_key:
            return False

        try:
            token = AccessToken.objects.get_token(access_key)
        except AccessToken.DoesNotExist:
            return False

        request.user = token.user
        return True


class AuthenticatedUserResource(ModelResource):

    events_accepted = fields.ListField(readonly=True)

    class Meta:
        queryset = SUser.objects.all()
        resource_name = 'authenticated_user'
        allowed_methods = ['get']

        excludes = ['password']

        authentication = OAuth2Authentication()

    def dehydrate_events_accepted(self, bundle):
        attends = Attend.objects.filter(user=bundle.obj).exclude(state=AttendState.waiting).select_related('event')
        return [attend.event.pk for attend in attends]

    def get_object_list(self, request):
        return super(AuthenticatedUserResource, self).get_object_list(request).filter(pk=request.user.pk)
