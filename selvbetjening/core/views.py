from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import AnonymousUser

def frontpage(request):
    if isinstance(request.user, AnonymousUser):
        return HttpResponseRedirect(reverse('auth_login'))
    else:
        return HttpResponseRedirect(reverse('members_profile'))

