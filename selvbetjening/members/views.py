# coding=UTF-8

from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required

from forms import ProfileForm, ProfileChangeEmailForm, EmailChangeRequest

@login_required
def profile_edit(request,
                 template_name='members/profile_edit.html',
                 success_page='members_profile',
                 form_class=ProfileForm):
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            form.save(request.user)
            request.user.message_set.create(message=_(u'Personal information updated'))
            return HttpResponseRedirect(reverse(success_page))
    else:
        user = request.user
        user_profile = user.get_profile()
        form = form_class(initial={'first_name':user.first_name,
                                   'last_name':user.last_name,
                                   'dateofbirth':user_profile.dateofbirth.strftime('%d-%m-%Y'),
                                   'street':user_profile.street,
                                   'city':user_profile.city,
                                   'postalcode':user_profile.postalcode,
                                   'phonenumber':user_profile.phonenumber,
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
            request.user.message_set.create(message=_(u'An email has been sent to your old email to verify your email change.'))
            return HttpResponseRedirect(reverse(success_page))
    else:
        form = form_class()

    return render_to_response(template_name, {'form' : form}, context_instance=RequestContext(request))

def profile_change_email_confirm(request,
                                 key,
                                 template_name='members/profile_change_email_done.html'):

    result = EmailChangeRequest.objects.confirm(key)

    return render_to_response(template_name, {'success' : result}, context_instance=RequestContext(request))