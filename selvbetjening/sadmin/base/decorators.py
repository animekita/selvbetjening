from django.contrib.auth.decorators import user_passes_test
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.functional import lazy

def sadmin_access_required(view_func):

    def _wrapped_view(request, *args, **kwargs):
        if getattr(settings, 'SADMIN_USE_NATIVE_LOGIN', False):
            login_url = None
        else:
            login_url = reverse('sadmin:login')

        login_decorator = user_passes_test(
            lambda user: user.is_authenticated() and user.is_active and user.is_staff,
            login_url=login_url,
        )

        wrapped_login = login_decorator(view_func)

        return wrapped_login(request, *args, **kwargs)

    return _wrapped_view