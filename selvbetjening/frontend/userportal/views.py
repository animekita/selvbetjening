# coding=UTF-8
from django.forms import inlineformset_factory

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404
from django.contrib.formtools.preview import FormPreview
from django.contrib import messages
from django.contrib.auth import login, authenticate, get_user_model
from selvbetjening.core.members.models import UserWebsite

from selvbetjening.core.user.models import SUser
from selvbetjening.core.members.forms import UserRegistrationForm, ProfileEditForm, UserWebsiteFormSetBase
from selvbetjening.frontend.userportal.forms import ChangePasswordForm, ChangePictureForm, \
    PrivacyForm, ChangeUsernameForm
from selvbetjening.frontend.userportal.processor_handlers import profile_page_processors
from selvbetjening.frontend.userportal.models import UserPrivacy


def profile_redirect(request):
    if isinstance(request.user, AnonymousUser):
        return HttpResponseRedirect(reverse('members_login'))
    else:
        return HttpResponseRedirect(reverse('members_profile'))


@login_required
def public_profile_page(request,
                        username,
                        template_name='userportal/public_profile.html',
                        template_no_access_name='userportal/profile_no_access.html'):

    user = get_object_or_404(SUser, username=username)
    privacy, created = UserPrivacy.objects.get_or_create(user=user)

    own_profile = False

    if privacy.public_profile:
        handler = profile_page_processors.get_handler(request, user)
        add_to_profile = handler.view(own_profile)

        return render(template_name,
                      {
                          'viewed_user' : user,
                          'privacy' : privacy,
                          'add_to_profile' : add_to_profile
                      })

    else:
        return render(request,
                      template_no_access_name,
                      {
                          'username': user.username
                      })


@login_required
def profile(request,
            template_name='userportal/profile.html'):

    user = request.user
    privacy = UserPrivacy.full_access()

    own_profile = True
    own_privacy, created = UserPrivacy.objects.get_or_create(user=user)

    handler = profile_page_processors.get_handler(request, user)
    add_to_profile = handler.view(own_profile)

    return render(request,
                  template_name,
                  {
                      'viewed_user': user,
                      'privacy': privacy,
                      'own_privacy': own_privacy,
                      'add_to_profile': add_to_profile
                  })


@login_required
def edit_profile(request,
                 template_name='userportal/edit_profile.html',
                 success_page='userportal_profile',
                 form_class=ProfileEditForm):

    UserWebsiteFormSet = inlineformset_factory(get_user_model(), UserWebsite, formset=UserWebsiteFormSetBase, extra=2)

    user = request.user

    if request.method == 'POST':
        form = form_class(request.POST, instance=user)
        website_form = UserWebsiteFormSet(request.POST, instance=user)

        if form.is_valid() and website_form.is_valid():
            form.save()
            website_form.save()

            messages.success(request, _(u'Personal information updated'))
            return HttpResponseRedirect(reverse(success_page))
    else:
        form = form_class(instance=user)
        website_form = UserWebsiteFormSet(instance=user)

    return render(request,
                  template_name,
                  {
                      'form': form,
                      'website_form': website_form
                  })


@login_required
def edit_privacy(request,
                 form_class=PrivacyForm,
                 template_name='userportal/edit_privacy.html',
                 success_page='userportal_profile'):

    privacy, created = UserPrivacy.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = form_class(request.POST, instance=privacy)
        if form.is_valid:

            form.save()

            messages.success(request, _(u'Privacy settings updated'))
            return HttpResponseRedirect(reverse(success_page))

    else:
        form = form_class(instance=privacy)

    return render(request,
                  template_name,
                  {
                      'form': form
                  })


@login_required
def edit_picture(request,
                 form_class=ChangePictureForm,
                 success_page='userportal_profile',
                 template_name='userportal/edit_picture.html'):

    profile = request.user

    if request.method == 'POST':
        form = form_class(data=request.POST, files=request.FILES)

        if form.is_valid():

            profile.picture = form.cleaned_data['picture']
            profile.save()

            messages.success(request, _(u'Profile picture changed'))
            return HttpResponseRedirect(reverse(success_page))

    else:
        form = form_class()

    return render(request,
                  template_name,
                  {
                      'form': form,
                      'user': profile
                  })


@login_required
def edit_password(request,
                  template_name='userportal/edit_password.html',
                  post_change_redirect='userportal_profile',
                  change_password_form=ChangePasswordForm):

    if request.method == 'POST':
        form = change_password_form(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _(u'Password changed'))
            return HttpResponseRedirect(reverse(post_change_redirect))
    else:
        form = change_password_form(request.user)

    return render(request,
                  template_name,
                  {
                      'form': form,
                  })


class UsernameChangeView(FormPreview):
    preview_template = 'userportal/edit_username_confirmed.html'
    form_template = 'userportal/edit_username.html'

    def __call__(self, request, *args, **kwargs):
        return super(UsernameChangeView, self).__call__(request, *args, **kwargs)

    def process_preview(self, request, form, context):
        context['new_username'] = form.cleaned_data['new_username']

    def done(self, request, cleaned_data):

        request.user.username = cleaned_data['new_username']
        request.user.save()

        messages.success(request, _(u'Username changed'))
        return HttpResponseRedirect(reverse('userportal_profile'))

edit_username = login_required(UsernameChangeView(ChangeUsernameForm))


def register(request,
             success_page,
             form_class=UserRegistrationForm,
             login_on_success=False,
             template_name='userportal/registration.html'):

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
                user = authenticate(username=user.username, password=request.POST['password'])
                login(request, user)

            if callable(success_page):
                return HttpResponseRedirect(success_page(request, user))
            else:
                return HttpResponseRedirect(reverse(success_page))
    else:
        form = form_class()

    return render(request,
                  template_name,
                  {
                      'form': form
                  })