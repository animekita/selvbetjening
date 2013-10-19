
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.urlresolvers import reverse_lazy


def sadmin_prerequisites(function):
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated() and u.is_staff and u.is_superuser,
        login_url=reverse_lazy('sadmin2:login'),
        redirect_field_name=REDIRECT_FIELD_NAME
    )
    return actual_decorator(function)
