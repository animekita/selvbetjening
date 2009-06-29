from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

def eventmode_required(view_func):
    def check_eventmode(request, *args, **kwargs):
        if request.eventmode.is_authenticated():
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('eventmode_login'))

    return check_eventmode