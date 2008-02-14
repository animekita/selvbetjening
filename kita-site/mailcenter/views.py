from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required, permission_required

from mailcenter.models import Mail
from mailcenter.forms import CreateMailForm, EditMailForm, SendPreviewEmailForm

@permission_required('mailcenter.add_mail')
def list_mails(request, template_name='mailcenter/list.html', form_class=CreateMailForm):

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
def send_mails(request, mail_id, template_name='mailcenter/send.html'):
    mail = get_object_or_404(Mail, pk=mail_id)
    
    return render_to_response(template_name,
                              {'form' : form, 'mail' : args.get('instance', None)},
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
