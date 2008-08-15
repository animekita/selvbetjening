# coding=UTF-8

"""
Views which allow users to create and activate accounts.

"""
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.contrib.auth import login, authenticate

from eventmode.decorators import eventmode_required
from core import messaging

from models import RegistrationProfile
from forms import CreateForm

def activate(request, activation_key, template_name='registration/activate.html'):
    """ Activates a ``User``'s account, if their key is valid and hasn't expired. """

    activation_key = activation_key.lower() # Normalize before trying anything with it.
    account = RegistrationProfile.objects.activate_user(activation_key)
    return render_to_response(template_name,
                              { 'account': account,
                                'success': not account == False,
                                'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS },
                              context_instance=RequestContext(request))


def register(request, success_page='registration_complete',
             form_class=CreateForm,
             template_name='registration/registration_form.html'):
    """ Allows a new user to register an account. """

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(success_page))
    else:
        form = form_class()

    return render_to_response(template_name,
                              { 'form': form },
                              context_instance=RequestContext(request))

@eventmode_required
def create_and_signup(request,
             form_class=CreateForm,
             template_name='registration/registration_form.html'):

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            form.save()
            login(request, authenticate(username=form.cleaned_data['username'],
                                        password=form.cleaned_data['password1']))
            messaging.write(request, _('Your user account has been created.'))
            return HttpResponseRedirect(reverse('events_signup',
                                                kwargs={'event_id' : request.eventmode.get_model().event.id}))
    else:
        form = form_class()

    return render_to_response(template_name,
                              { 'form': form },
                              context_instance=RequestContext(request))