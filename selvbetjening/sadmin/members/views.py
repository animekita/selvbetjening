from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils.translation import ugettext as _
import operator
from django.contrib import messages

from selvbetjening.data.members.forms import ProfileForm, RegistrationForm
from selvbetjening.sadmin.base.sadmin import SAdminContext

from forms import AccessForm

def _search(request):
    query = request.GET.get('search', None)
    qs = []

    search_fields = ['first_name', 'last_name', 'username']

    if query is not None:
        qs = User.objects.all()

        for term in query.split():
            or_queries = [Q(**{'%s__icontains' % field_name: term}) for field_name in search_fields]
            qs = qs.filter(reduce(operator.or_, or_queries))

    return (query, qs)

def list(request,
         template_name='sadmin/members/list.html'):

    query, qs = _search(request)

    return render_to_response(template_name,
                              {'query' : query,
                               'users' : qs},
                              context_instance=SAdminContext(request))

def view(request,
         username,
         template_name='sadmin/members/view.html'):

    user = get_object_or_404(User, username=username)

    if request.method == 'POST':
        form = ProfileForm(user, request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, _(u'Personal information updated'))
    else:
        form = ProfileForm(user)

    return render_to_response(template_name,
                              {'user' : user,
                               'form' : form},
                              context_instance=SAdminContext(request))

def view_access(request,
                username,
                template_name='sadmin/members/view_access.html'):

    user = get_object_or_404(User, username=username)

    if request.method == 'POST':
        form = AccessForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, _(u'Member access updated'))
    else:
        form = AccessForm(instance=user)

    return render_to_response(template_name,
                              {'user': user,
                               'form': form},
                              context_instance=SAdminContext(request))

def create(request,
           template_name='sadmin/members/create.html'):

    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            messages.success(request, _(u'Member created'))
            return HttpResponseRedirect(reverse('sadmin:members_view',
                                                kwargs={'username': user.username}))
    else:
        form = RegistrationForm()

    return render_to_response(template_name,
                              {'form': form},
                              context_instance=SAdminContext(request))

def ajax_search(request,
                template_name='sadmin/members/ajax/search.html'):
    query, qs = _search(request)

    return render_to_response(template_name,
                              {'query' : query,
                               'users' : qs},
                              context_instance=SAdminContext(request))
