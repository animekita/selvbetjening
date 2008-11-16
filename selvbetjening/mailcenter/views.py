from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required, permission_required

from mailcenter.models import Mail
from mailcenter.forms import CreateMailForm, EditMailForm, SendPreviewEmailForm, SelectGroupForm, ConfirmGroupForm

@permission_required('mailcenter.add_mail')
def list_mails(request,
               template_name='mailcenter/list.html',
               form_class=CreateMailForm):

    form = form_class()

    if request.method == 'POST':
        return HttpResponseRedirect(reverse('mailcenter_edit', kwargs={'mail_id' : 'new'}))

    return render_to_response(template_name,
                              {'mails' : Mail.objects.all(), 'form' : form},
                              context_instance=RequestContext(request))

@permission_required('mailcenter.add_mail')
def show_mail(request, mail_id, template_name='mailcenter/view.html'):
    mail = get_object_or_404(Mail, pk=mail_id)

    return render_to_response(template_name,
                              {'mail' : mail},
                              context_instance=RequestContext(request))

@permission_required('mailcenter.add_mail')
def edit_mail(request, mail_id, template_name='mailcenter/edit.html', form_class=EditMailForm):

    args = {}

    if mail_id != 'new':
        mail = get_object_or_404(Mail, pk=mail_id)
        if not mail.is_draft():
            raise Http404

        args['instance'] = mail

    if request.method == 'POST':
        form = form_class(request.POST, **args)
        if form.is_valid():
            mail = form.save()
            return HttpResponseRedirect(reverse('mailcenter_edit', kwargs={'mail_id' : mail.id}))
    else:
        form = form_class(**args)

    return render_to_response(template_name,
                              {'form' : form, 'mail' : args.get('instance', None)},
                              context_instance=RequestContext(request))

@permission_required('mailcenter.add_mail')
def send_mails(request, mail_id, select_group='mailcenter/send.html',
               confirm_recipients='mailcenter/send_confirm.html', select_form_class=SelectGroupForm,
               confirm_form_class=ConfirmGroupForm):
    mail = get_object_or_404(Mail, pk=mail_id)

    if request.method == 'POST':
        form = SelectGroupForm(request.POST)

        if form.is_valid():
            next_form = confirm_form_class(request.POST)
            recipients = form.get_selected_recipients()
            accept, deny = mail.recipient_filter(recipients)

            if next_form.is_valid():
                mail.send_mail_to_users(accept)
                request.user.message_set.create(message=_(u"E-mails have been sent to %s persons") % len(accept))
                return HttpResponseRedirect(reverse('mailcenter_list'))
            else:
                return render_to_response(confirm_recipients,
                              {'mail' : mail, 'accept' : accept, 'deny' : deny, 'form' : next_form},
                              context_instance=RequestContext(request))
    else:
        form = SelectGroupForm()

    return render_to_response(select_group,
                              {'form' : form, 'mail' : mail},
                              context_instance=RequestContext(request))

@permission_required('mailcenter.add_mail')
def send_test_mail(request, mail_id, template_name='mailcenter/preview.html', form_class=SendPreviewEmailForm):
    mail = get_object_or_404(Mail, pk=mail_id)

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            mail.send_mail([form.cleaned_data['email']])
            request.user.message_set.create(message=_(u"A draft email has been sent to %s" % form.cleaned_data['email']))
            return HttpResponseRedirect(reverse('mailcenter_list'))
    else:
        form = form_class()

    return render_to_response(template_name,
                              {'form' : form, 'mail' : mail},
                              context_instance=RequestContext(request))
