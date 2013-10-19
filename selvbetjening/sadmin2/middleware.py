
from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.core.urlresolvers import reverse_lazy

import re


class RequireLoginMiddleware(object):
    """
    Extra login layer

    This piece of middleware protects the entire sadmin2 installation by refusing unauthorized access to any url
    starting with the sadmin2 base url.

    Two assumptions are made:
    1. The sadmin2 installation is included under settings.SADMIN2_BASE_URL
    2. sadmin2:login reverses to the correct login url.

    The purpose of this middleware is NOT to replace the usual authorization decorators, but to function as an
    addition to these. If a decorator is missing or an error causes the decorators to fail, then this middleware
    will still protect the pages. Likewise, if this middleware somehow fails then the decorators are still in place.

    The same database fields are used to check access to sadmin, however the logic has been negated on purpose (or not)
    and not (and) to decrease the chance of the same error resulting in a failure in both authentication mechanisms.
    """

    def __init__(self):
        self.sadmin2_url = re.compile('^/%s/' % settings.SADMIN2_BASE_URL)

    def process_request(self, request):
        if self.sadmin2_url.match(request.path):
            if request.path == reverse_lazy('sadmin2:login'):
                return

            if not request.user.is_authenticated() or not request.user.is_staff or not request.user.is_superuser:
                return redirect_to_login(
                    request.build_absolute_uri(),
                    reverse_lazy('sadmin2:login'))