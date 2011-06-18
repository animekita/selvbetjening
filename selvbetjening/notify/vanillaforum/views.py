from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from selvbetjening.portal.profile.forms import ChangePictureForm

from models import Settings
from forms import SettingsForm

@login_required
def picture_edit(request,
                 form_class=ChangePictureForm,
                 template_name='vanillaforum/picture_edit.html'):

    user_settings, created = Settings.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = form_class(data=request.POST, files=request.FILES)

        if form.is_valid():
            user_settings.picture = form.cleaned_data['picture']
            user_settings.save()

            request.user.message_set.create(message=_(u'Forum picture changed'))

    else:
        form = form_class()

    return render_to_response(template_name,
                              {'form': form,
                               'settings': user_settings},
                              context_instance=RequestContext(request))

@login_required
def notification_edit(request,
                      template_name='vanillaforum/notification_edit.html'):

    user_settings, created = Settings.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = SettingsForm(request.POST, instance=user_settings)

        if form.is_valid():
            form.save()
            request.user.message_set.create(message=_(u'Notification settings changed'))

    else:
        form = SettingsForm(instance=user_settings)

    return render_to_response(template_name,
                              {'form': form},
                              context_instance=RequestContext(request))
