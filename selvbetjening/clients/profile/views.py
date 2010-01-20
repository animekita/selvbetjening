# coding=UTF-8

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.contrib.auth.forms import PasswordChangeForm

from selvbetjening.data.members.forms import ProfileForm
from selvbetjening.data.members.models import UserProfile
from selvbetjening.data.events.models import Attend

from processor_handlers import viewprofile as viewprofile_handler

def profile_redirect(request):
    if isinstance(request.user, AnonymousUser):
        return HttpResponseRedirect(reverse('members_login'))
    else:
        return HttpResponseRedirect(reverse('members_profile'))

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
        try:
            user_profile = user.get_profile()
        except UserProfile.DoesNotExist:
            user_profile = UserProfile.objects.create(user=user)

        dateofbirth = None
        if user_profile.dateofbirth:
            dateofbirth = user_profile.dateofbirth.strftime('%d-%m-%Y')

        form = form_class(initial={'first_name':user.first_name,
                                   'last_name':user.last_name,
                                   'dateofbirth': dateofbirth ,
                                   'street':user_profile.street,
                                   'city':user_profile.city,
                                   'postalcode':user_profile.postalcode,
                                   'phonenumber':user_profile.phonenumber,
                                   'email':user.email
                                  })

    return render_to_response(template_name, {'form' : form}, context_instance=RequestContext(request))

@login_required
def password_change(request,
                    template_name='members/password_change.html',
                    post_change_redirect=None):

    if post_change_redirect is None:
        post_change_redirect = 'auth_password_change_done'

    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(post_change_redirect))
    else:
        form = PasswordChangeForm(request.user)

    return render_to_response(template_name,
                              {'form': form,},
                              context_instance=RequestContext(request))

@login_required
def current_events(request,
                   template_name='profile/events.html'):

    attends = Attend.objects.filter(user=request.user).select_related().order_by('-event__startdate')

    return render_to_response(template_name,
                              {'attends': attends},
                              context_instance=RequestContext(request))
