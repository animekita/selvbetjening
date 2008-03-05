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
from django.contrib.auth.decorators import permission_required

from django import oldforms

from registration.models import RegistrationProfile
from registration.forms import RegistrationForm

def activate(request, activation_key, template_name='registration/activate.html'):
    """
    Activates a ``User``'s account, if their key is valid and hasn't expired.
    
    """
    activation_key = activation_key.lower() # Normalize before trying anything with it.
    account = RegistrationProfile.objects.activate_user(activation_key)
    return render_to_response(template_name,
                              { 'account': account,
                                'success': not account == False,
                                'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS },
                              context_instance=RequestContext(request))


def register(request, success_page='registration_complete',
             form_class=RegistrationForm,
             template_name='registration/registration_form.html'):
    """
    Allows a new user to register an account.
    
    """
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            new_user = form.save()
            return HttpResponseRedirect(reverse(success_page))
    else:
        form = form_class()
        
    return render_to_response(template_name,
                              { 'form': form },
                              context_instance=RequestContext(request))

@permission_required('auth.add_user')
def create(request, success_page='user_created.html',
             form_class=RegistrationForm,
             template_name='registration/registration_form.html'):

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            new_user = form.save()
            return HttpResponseRedirect(reverse(success_page))
    else:
        form = form_class()
        
    return render_to_response(template_name,
                              { 'form': form },
                              context_instance=RequestContext(request))
