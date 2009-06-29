from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.admin import helpers

from models import Mail
from forms import SendPreviewEmailForm, SelectGroupForm, ConfirmGroupForm

@staff_member_required
def send(request, mail_id, select_group='admin/mailcenter/send.html',
               confirm_recipients='admin/mailcenter/send_confirm.html',
               select_form_class=SelectGroupForm,
               confirm_form_class=ConfirmGroupForm):
    mail = get_object_or_404(Mail, pk=mail_id)

    if request.method == 'POST':
        form = SelectGroupForm(request.POST)

        if form.is_valid():
            confirm_form = confirm_form_class(request.POST)
            recipients = form.get_selected_recipients()
            accepted_mails, denied_mails = mail.recipient_filter(recipients)

            if confirm_form.is_valid():
                mail.send(accepted_mails)
                request.user.message_set.create(message=_(u'E-mails have been sent to %s persons') % len(accepted_mails))
            else:
                return render_to_response(confirm_recipients,
                              {'mail' : mail, 'accept' : accepted_mails,
                               'deny' : denied_mails, 'adminform' : helpers.AdminForm(confirm_form,
                                                               [(None, {'fields': confirm_form.base_fields.keys()})],
                                                               {})},
                              context_instance=RequestContext(request))
    else:
        form = SelectGroupForm()

    return render_to_response(select_group,
                              {'adminform' : helpers.AdminForm(form,
                                                               [(None, {'fields': form.base_fields.keys()})],
                                                               {}),
                               'mail' : mail},
                              context_instance=RequestContext(request))

@staff_member_required
def send_preview(request, mail_id,
                 template_name='admin/mailcenter/send_preview.html',
                 form_class=SendPreviewEmailForm):
    mail = get_object_or_404(Mail, pk=mail_id)

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            mail.send_preview([form.cleaned_data['email'],])
            request.user.message_set.create(message=_(u'A preview e-mail has been sent to %s' % form.cleaned_data['email']))
    else:
        form = form_class()

    return render_to_response(template_name,
                              {'adminform' : helpers.AdminForm(form,
                                                               [(None, {'fields': form.base_fields.keys()})],
                                                               {}),
                               'mail' : mail},
                              context_instance=RequestContext(request))

@staff_member_required
def preview(request, mail_id,
            template_name='admin/mailcenter/preview.html'):

    mail = get_object_or_404(Mail, pk=mail_id)

    return render_to_response(template_name,
                              {'mail' : mail},
                              context_instance=RequestContext(request))