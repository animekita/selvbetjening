# coding=UTF-8

"""
Views which allow users to create accounts.

"""

from django.core.urlresolvers import reverse
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from selvbetjening.data.members.forms import RegistrationForm

def register(request,
             success_page='quickregistration_complete',
             form_class=RegistrationForm,
             login_on_success=False,
             template_name='quickregistration/registration_form.html'):
    """ Allows a new user to register an account.

    success_page -- a reversable view name or a function returning
                    an url. The function takes a request and a user
                    object as input.
    """

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            user = form.save()

            if login_on_success:
                login(request, user)

            if callable(success_page):
                return HttpResponseRedirect(success_page(request, user))
            else:
                return HttpResponseRedirect(reverse(success_page))
    else:
        form = form_class()

    return render_to_response(template_name,
                              { 'form': form },
                              context_instance=RequestContext(request))