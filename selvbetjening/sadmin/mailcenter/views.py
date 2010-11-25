from django.shortcuts import render_to_response
from django.contrib.auth.decorators import permission_required
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from selvbetjening.core.forms import form_collection_builder
from selvbetjening.sadmin.base.sadmin import SAdminContext
from selvbetjening.sadmin.base.decorators import sadmin_access_required
from selvbetjening.clients.mailcenter.models import EmailSpecification

from forms import EmailTemplateForm, EmailSourceForm, \
     SendPreviewEmailForm, SendNewsletterForm, conditionform_registry

#@sadmin_access_required
#@permission_required('mailcenter.change_emailspecification')
def list_emails(request,
                template_name='sadmin/mailcenter/list.html'):

    emails = EmailSpecification.objects.all()

    return render_to_response(template_name,
                              {'emails': emails},
                              context_instance=SAdminContext(request))

#@sadmin_access_required
#@permission_required('mailcenter.change_emailspecification')
def update_email(request,
                 email_pk=None):

    if email_pk is not None:
        email = get_object_or_404(EmailSpecification, pk=email_pk)
        template_name='sadmin/mailcenter/email/update.html'
    else:
        email = None
        template_name='sadmin/mailcenter/create.html'

    if request.method == 'POST':
        form = EmailTemplateForm(request.POST, instance=email)

        if form.is_valid():
            saved = form.save()

            if email is None:
                messages.success(request, _(u'E-mail specification successfully saved'))
                return HttpResponseRedirect(
                    reverse('sadmin:mailcenter_email_update', kwargs={'email_pk': saved.pk}))
            else:
                messages.success(request, _(u'E-mail specification sucessfully updated'))

    else:
        form = EmailTemplateForm(instance=email)

    return render_to_response(template_name,
                              {'form': form,
                               'email': email},
                              context_instance=SAdminContext(request))

#@sadmin_access_required
#@permission_required('mailcenter.change_emailspecification')
def bind_email(request,
               email_pk,
               template_name='sadmin/mailcenter/email/bind.html'):

    email = get_object_or_404(EmailSpecification, pk=email_pk)

    if request.method == 'POST':
        form = EmailSourceForm(request.POST, instance=email)

        if form.is_valid():
            form.save()
            messages.success(request, _(u'E-mail specification successfully updated'))

    else:
        form = EmailSourceForm(instance=email)

    return render_to_response(template_name,
                              {'form': form,
                               'email': email},
                              context_instance=SAdminContext(request))

#@sadmin_access_required
#@permission_required('mailcenter.change_emailspecification')
def preview_email(request,
                  email_pk,
                  template_name='sadmin/mailcenter/email/preview.html'):

    email = get_object_or_404(EmailSpecification, pk=email_pk)

    if request.method == 'POST':
        form = SendPreviewEmailForm(request.POST)

        if form.is_valid():
            user = form.cleaned_data['user']

            email.send_email(user, bypass_conditions=True)
            messages.success(request, _(u'E-mail preview successfully sent to %s') % user.get_full_name())

            form = SendPreviewEmailForm()

    else:
        form = SendPreviewEmailForm()

    return render_to_response(template_name,
                              {'form': form,
                               'email': email},
                              context_instance=SAdminContext(request))

#@sadmin_access_required
#@permission_required('mailcenter.change_emailspecification')
def send_email(request,
               email_pk,
               template_name='sadmin/mailcenter/email/send.html',
               template_name_bound='sadmin/mailcenter/email/email-bound.html'):

    email = get_object_or_404(EmailSpecification, pk=email_pk)

    if len(email.event) > 0:
        # can't send newsletter when bound to event
        return render_to_response(template_name_bound,
                                  {'email': email,},
                                  context_instance=SAdminContext(request))

    recipients = User.objects.filter(userprofile__send_me_email=True)

    if request.method == 'POST':
        form = SendNewsletterForm(request.POST)

        if  form.is_valid():
            email.send_email(recipients)
            messages.success(request, _(u'Newsletter sucessfully sent to %s receipients') % len(recipients))

            form = SendNewsletterForm()

    else:
        form = SendNewsletterForm()

    return render_to_response(template_name,
                              {'form': form,
                               'email': email,
                               'recipients': recipients},
                              context_instance=SAdminContext(request))

#@sadmin_access_required
#@permission_required('mailcenter.change_emailspecification')
def filter_email(request,
                 email_pk,
                 template_name='sadmin/mailcenter/email/filter.html'):

    email = get_object_or_404(EmailSpecification, pk=email_pk)

    form_classes = conditionform_registry.get_forms(email.conditions)
    ConditionForms = form_collection_builder(form_classes)

    if request.method == 'POST':
        forms = ConditionForms(request.POST, email_specification=email)

        if forms.is_valid():
            forms.save()

            messages.success(request, _(u'Filter successfully updated'))

    else:
        forms = ConditionForms(email_specification=email)

    return render_to_response(template_name,
                              {'email': email,
                               'forms': forms,},
                              context_instance=SAdminContext(request))
