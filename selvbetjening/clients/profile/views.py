# coding=UTF-8

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from selvbetjening.data.members.forms import ProfileForm
from selvbetjening.data.members.models import UserProfile
from selvbetjening.data.events.models import Attend

from forms import ChangePasswordForm, ChangePictureForm
from processor_handlers import profile_page_processors

def profile_redirect(request):
    if isinstance(request.user, AnonymousUser):
        return HttpResponseRedirect(reverse('members_login'))
    else:
        return HttpResponseRedirect(reverse('members_profile'))

@login_required
def profile_page(request,
                 template_name= 'profile/profile.html'):

    handler = profile_page_processors.get_handler(request, request.user)
    add_to_profile = handler.view()

    return render_to_response(template_name,
                              {'add_to_profile' : add_to_profile,},
                              context_instance=RequestContext(request))

@login_required
def profile_edit(request,
                 template_name='profile/profile_edit.html',
                 success_page='members_profile',
                 form_class=ProfileForm):
    if request.method == 'POST':
        form = form_class(request.user, request.POST)
        if form.is_valid():
            form.save()
            request.user.message_set.create(message=_(u'Personal information updated'))
            return HttpResponseRedirect(reverse(success_page))
    else:
        form = form_class(request.user)

    return render_to_response(template_name,
                              {'form' : form},
                              context_instance=RequestContext(request))

@login_required
def picture_edit(request,
                 form_class=ChangePictureForm,
                 template_name='profile/picture_edit.html'):

    if request.method == 'POST':
        form = form_class(data=request.POST, files=request.FILES)

        if form.is_valid():
            profile = request.user.get_profile()
            profile.picture = form.cleaned_data['picture']
            profile.save()

    else:
        form = form_class()

    return render_to_response(template_name,
                              {'form': form},
                              context_instance=RequestContext(request))

@login_required
def password_change(request,
                    template_name='profile/password_change.html',
                    post_change_redirect=None,
                    change_password_form=ChangePasswordForm):

    if post_change_redirect is None:
        post_change_redirect = 'auth_password_change_done'

    if request.method == 'POST':
        form = change_password_form(request.user, request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(post_change_redirect))
    else:
        form = change_password_form(request.user)

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
