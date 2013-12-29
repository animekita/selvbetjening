
from tastypie.authentication import Authentication
from tastypie.resources import ModelResource

from provider.oauth2.models import AccessToken

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
    class Meta:
        queryset = SUser.objects.all()
        resource_name = 'authenticated_user'
        allowed_methods = ['get']

        excludes = ['password']

        authentication = OAuth2Authentication()

    def get_object_list(self, request):
        return super(AuthenticatedUserResource, self).get_object_list(request).filter(pk=1)
