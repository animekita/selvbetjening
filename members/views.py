# coding=UTF-8

"""
Views which allow users to create and activate accounts.

"""
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse

from django import oldforms

from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.decorators import login_required

from members.forms import RegistrationForm, ProfileForm, ProfileChangeEmailForm, PasswordChangeForm
from members.models import RegistrationProfile, EmailChangeRequest

from events.models import Event

def activate(request, activation_key, template_name='registration/activate.html'):
    """
    Activates a ``User``'s account, if their key is valid and hasn't
    expired.
    
    By default, uses the template ``registration/activate.html``; to
    change this, pass the name of a template as the keyword argument
    ``template_name``.
    
    Context:
    
        account
            The ``User`` object corresponding to the account, if the
            activation was successful. ``False`` if the activation was
            not successful.
    
        expiration_days
            The number of days for which activation keys stay valid
            after registration.
    
    Template:
    
        registration/activate.html or ``template_name`` keyword
        argument.
    
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
    
    Following successful registration, redirects to either
    ``/accounts/register/complete/`` or, if supplied, the URL
    specified in the keyword argument ``success_url``.
    
    By default, ``registration.forms.RegistrationForm`` will be used
    as the registration form; to change this, pass a different form
    class as the ``form_class`` keyword argument. The form class you
    specify must have a method ``save`` which will create and return
    the new ``User``, and that method must accept the keyword argument
    ``profile_callback`` (see below).
    
    To enable creation of a site-specific user profile object for the
    new user, pass a function which will create the profile object as
    the keyword argument ``profile_callback``. See
    ``RegistrationManager.create_inactive_user`` in the file
    ``models.py`` for details on how to write this function.
    
    By default, uses the template
    ``registration/registration_form.html``; to change this, pass the
    name of a template as the keyword argument ``template_name``.
    
    Context:
    
        form
            The registration form.
    
    Template:
    
        registration/registration_form.html or ``template_name``
        keyword argument.
    
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

@login_required
def profile(request, template_name='registration/profile.html'):

    visited = request.user.event_set.all()
    visited_keys = []
    for event in visited:
        visited_keys.append(event.id)

    return render_to_response(template_name, 
                              {'events_visited' : visited,
                                'events_new' : Event.objects.exclude(id__in=visited_keys).filter(registration_open__exact=1) },
                              context_instance=RequestContext(request))

@login_required
def profile_edit(request, 
                 template_name='registration/profile_edit.html',
                 success_page='members_profile',
                 form_class=ProfileForm):
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            form.save(request.user)
            request.user.message_set.create(message="Stamoplysninger opdateret")
            return HttpResponseRedirect(reverse(success_page))
    else:
        user = request.user
        profile = user.get_profile()
        form = form_class(initial={'first_name':user.first_name, 
                                   'last_name':user.last_name, 
                                   'dateofbirth':profile.dateofbirth,
                                   'street':profile.street,
                                   'city':profile.city,
                                   'postalcode':profile.postalcode,
                                   'phonenumber':profile.phonenumber,
                                  })
    
    return render_to_response(template_name, {'form' : form}, context_instance=RequestContext(request))

@login_required
def profile_change_email(request,
                         template_name='registration/profile_change_email.html',
                         success_page='members_profile',
                         form_class=ProfileChangeEmailForm):

    if request.method == 'POST':
        form = form_class(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            request.user.message_set.create(message=u'En email er blevet send till dig, følg instrukserne i denne.')
            return HttpResponseRedirect(reverse(success_page))
    else:
        form = form_class()
    
    return render_to_response(template_name, {'form' : form }, context_instance=RequestContext(request))

def profile_change_email_confirm(request, 
                                 key,
                                 template_name='registration/profile_change_email_done.html'):
    
    result = EmailChangeRequest.objects.confirm(key)
    
    return render_to_response(template_name, { 'success' : result }, context_instance=RequestContext(request))

@login_required
def password_change(request, template_name='registration/password_change_form.html', success_page='members_profile'):
    
    if request.method == "POST":
        form = PasswordChangeForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            request.user.message_set.create(message=u'Dit kodeord er blevet skiftet')
            return HttpResponseRedirect(reverse(success_page))
    else:
        form = PasswordChangeForm(user=request.user)
        
    return render_to_response(template_name, {'form' : form},
        context_instance=RequestContext(request))