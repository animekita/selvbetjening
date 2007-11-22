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

from django import oldforms

from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.decorators import login_required

from members.forms import ProfileForm, ProfileChangeEmailForm, PasswordChangeForm, EmailChangeRequest
from registration.models import RegistrationProfile

from events.models import Event

@login_required
def profile(request, template_name='members/profile.html'):

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
                 template_name='members/profile_edit.html',
                 success_page='members_profile',
                 form_class=ProfileForm):
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            form.save(request.user)
            request.user.message_set.create(message=_(u"Personal information updated"))
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
                         template_name='members/profile_change_email.html',
                         success_page='members_profile',
                         form_class=ProfileChangeEmailForm):

    if request.method == 'POST':
        form = form_class(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            request.user.message_set.create(message=_(u"An email has been sent to you containing further instructions to activate your account."))
            return HttpResponseRedirect(reverse(success_page))
    else:
        form = form_class()
    
    return render_to_response(template_name, {'form' : form }, context_instance=RequestContext(request))

def profile_change_email_confirm(request, 
                                 key,
                                 template_name='members/profile_change_email_done.html'):
    
    result = EmailChangeRequest.objects.confirm(key)
    
    return render_to_response(template_name, { 'success' : result }, context_instance=RequestContext(request))

@login_required
def password_change(request, template_name='members/password_change_form.html', success_page='members_profile'):
    
    if request.method == "POST":
        form = PasswordChangeForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            request.user.message_set.create(message=_(u"Your password have been changed"))
            return HttpResponseRedirect(reverse(success_page))
    else:
        form = PasswordChangeForm(user=request.user)
        
    return render_to_response(template_name, {'form' : form},
        context_instance=RequestContext(request))