# coding=UTF-8

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser, User
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404
from django.contrib.formtools.preview import FormPreview
from django.contrib import messages

from selvbetjening.core.members.forms import ProfileForm
from selvbetjening.core.events.models import Attend

from forms import ChangePasswordForm, ChangePictureForm, PrivacyForm, ChangeUsernameForm
from processor_handlers import profile_page_processors
from models import UserPrivacy

def profile_redirect(request):
    if isinstance(request.user, AnonymousUser):
        return HttpResponseRedirect(reverse('members_login'))
    else:
        return HttpResponseRedirect(reverse('members_profile'))

@login_required
def public_profile_page(request,
                        username,
                        template_name='profile/public_profile.html',
                        template_no_access_name='profile/profile_no_access.html'):

    user = get_object_or_404(User, username=username)
    privacy, created = UserPrivacy.objects.get_or_create(user=user)

    own_profile = False

    if privacy.public_profile:
        handler = profile_page_processors.get_handler(request, user)
        add_to_profile = handler.view(own_profile)

        return render_to_response(template_name,
                                  {'viewed_user' : user,
                                   'privacy' : privacy,
                                   'add_to_profile' : add_to_profile,},
                                  context_instance=RequestContext(request))

    else:
        return render_to_response(template_no_access_name,
                                  {'username' : user.username},
                                  context_instance=RequestContext(request))

@login_required
def profile_page(request,
                 template_name='profile/profile.html'):

    user = request.user
    privacy = UserPrivacy.full_access()

    own_profile = True
    own_privacy, created = UserPrivacy.objects.get_or_create(user=user)

    handler = profile_page_processors.get_handler(request, user)
    add_to_profile = handler.view(own_profile)

    return render_to_response(template_name,
                              {'viewed_user' : user,
                               'privacy' : privacy,
                               'own_privacy' : own_privacy,
                               'add_to_profile' : add_to_profile,},
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
            messages.add_message(request, messages.INFO, _(u'Personal information updated'))
            return HttpResponseRedirect(reverse(success_page))
    else:
        form = form_class(request.user)

    return render_to_response(template_name,
                              {'form' : form},
                              context_instance=RequestContext(request))

@login_required
def privacy_edit(request,
                 form_class=PrivacyForm,
                 template_name='profile/privacy_edit.html',
                 success_page='members_profile'):

    privacy, created = UserPrivacy.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = form_class(request.POST, instance=privacy)
        if form.is_valid:
            form.save()
            messages.add_message(request, messages.INFO, _(u'Privacy settings updated'))
            return HttpResponseRedirect(reverse(success_page))

    else:
        form = form_class(instance=privacy)

    return render_to_response(template_name,
                              {'form': form},
                              context_instance=RequestContext(request))

@login_required
def picture_edit(request,
                 form_class=ChangePictureForm,
                 success_page='members_profile',
                 template_name='profile/picture_edit.html'):

    if request.method == 'POST':
        form = form_class(data=request.POST, files=request.FILES)

        if form.is_valid():
            profile = request.user.get_profile()
            profile.picture = form.cleaned_data['picture']
            profile.save()

            messages.add_message(request, messages.INFO, _(u'Profile picture changed'))
            return HttpResponseRedirect(reverse(success_page))

    else:
        form = form_class()

    return render_to_response(template_name,
                              {'form': form},
                              context_instance=RequestContext(request))

@login_required
def password_change(request,
                    template_name='profile/password_change.html',
                    post_change_redirect='members_profile',
                    change_password_form=ChangePasswordForm):

    if request.method == 'POST':
        form = change_password_form(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, _(u'Password changed'))
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

class UsernameChangeView(FormPreview):
    preview_template = 'profile/username_change_confirm.html'
    form_template = 'profile/username_change.html'

    def __call__(self, request, *args, **kwargs):
        return super(UsernameChangeView, self).__call__(request, *args, **kwargs)

    def process_preview(self, request, form, context):
        context['new_username'] = form.cleaned_data['new_username']

    def done(self, request, cleaned_data):
        old_username = request.user.username

        request.user.username = cleaned_data['new_username']
        request.user.save()

        messages.add_message(request, messages.INFO, _(u'Username changed'))
        return HttpResponseRedirect(reverse('members_profile'))

username_change = login_required(UsernameChangeView(ChangeUsernameForm))
