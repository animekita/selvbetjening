import operator

from django.shortcuts import render_to_response
from django.db.models import Q
from django.contrib.auth import logout as do_logout
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import views as auth_views
from django.contrib.auth import REDIRECT_FIELD_NAME

from selvbetjening.portal.profile.forms import LoginForm
from selvbetjening.sadmin.base.sadmin import SAdminContext
from selvbetjening.sadmin.base.decorators import sadmin_access_required

@sadmin_access_required
def dashboard(request,
              template_name='sadmin/base/dashboard.html'):

    return render_to_response(template_name,
                              context_instance=SAdminContext(request))

@sadmin_access_required
def logout(request):

    do_logout(request)

    messages.success(request, _(u'User sucessfully logged out'))

    return HttpResponseRedirect(reverse('sadmin:login'))

def login(request):
    class ObjectWrapper(object):
        def __init__(self, obj):
            self.obj = obj

        def __getattribute__(self, name):
            try:
                return super(ObjectWrapper, self).__getattribute__(name)
            except AttributeError:
                return self.obj.__getattribute__(name)

    wrapped_request = ObjectWrapper(request)

    if request.REQUEST.get(REDIRECT_FIELD_NAME, None) is None:
        wrapped_request.REQUEST = request.GET.copy()
        wrapped_request.REQUEST[REDIRECT_FIELD_NAME] = reverse('sadmin:dashboard')

    return auth_views.login(wrapped_request,
                            template_name='sadmin/base/login.html',
                            authentication_form=LoginForm)

def generic_search_page_unsecure(request,
                                 search_fields,
                                 queryset,
                                 template_name,
                                 default_to_empty_queryset=True,
                                 extra_context=None):

    query = request.GET.get('search', None)

    if query is not None and len(query.strip()) == 0:
        query = None

    if default_to_empty_queryset and query is None:
        qs = []
    else:
        qs = queryset() if callable(queryset) else queryset

    if query is not None:
        for term in query.split():
            or_queries = [Q(**{'%s__icontains' % field_name: term}) for field_name in search_fields]
            qs = qs.filter(reduce(operator.or_, or_queries))

    context = {'query' : query, 'queryset' : qs}

    if extra_context is not None:
        context.update(extra_context)

    return render_to_response(template_name,
                              context,
                              context_instance=SAdminContext(request))