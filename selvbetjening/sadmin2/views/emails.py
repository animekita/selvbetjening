
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils.translation import ugettext as _
from django.contrib import messages

from mailqueue.models import MailerMessage

from selvbetjening.core.mailcenter.models import EmailSpecification

from selvbetjening.sadmin2.views.generic import search_view, generic_create_view
from selvbetjening.sadmin2 import menu
from selvbetjening.sadmin2.decorators import sadmin_prerequisites
from selvbetjening.sadmin2.forms import TemplateForm, UserSelectorForm, AttendeeSelectorForm


@sadmin_prerequisites
def queue(request):

    queryset = MailerMessage.objects.all().\
        order_by('subject', 'last_attempt', '-pk')

    columns = ('subject', 'app', 'to_address')

    context = {
        'sadmin2_menu_main_active': 'emails',
        'sadmin2_breadcrumbs_active': 'emails_queue',
        'sadmin2_menu_tab': menu.sadmin2_menu_tab_emails,
        'sadmin2_menu_tab_active': 'queue',
    }

    return search_view(request,
                       queryset,
                       'sadmin2/emails/queue_list.html',
                       'sadmin2/emails/queue_list_inner.html',
                       search_columns=columns,
                       context=context)


@sadmin_prerequisites
def templates(request):

    queryset = EmailSpecification.objects.all().\
        order_by('-pk')

    columns = ('subject',)

    context = {
        'sadmin2_menu_main_active': 'emails',
        'sadmin2_breadcrumbs_active': 'emails_templates',
        'sadmin2_menu_tab': menu.sadmin2_menu_tab_emails,
        'sadmin2_menu_tab_active': 'templates'
    }

    return search_view(request,
                       queryset,
                       'sadmin2/emails/templates_list.html',
                       'sadmin2/emails/templates_list_inner.html',
                       search_columns=columns,
                       context=context)


@sadmin_prerequisites
def template(request, template_pk):

    instance = get_object_or_404(EmailSpecification, pk=template_pk)

    context = {
        'sadmin2_menu_main_active': 'emails',
        'sadmin2_breadcrumbs_active': 'emails_template',
        'sadmin2_menu_tab': menu.sadmin2_menu_tab_template,
        'sadmin2_menu_tab_active': 'template',

        'template': instance
    }

    return generic_create_view(request,
                               TemplateForm,
                               reverse('sadmin2:emails_template', kwargs={'template_pk': instance.pk}),
                               message_success=_('Template saved'),
                               context=context,
                               instance=instance)


@sadmin_prerequisites
def template_preview(request, template_pk):

    template_instance = get_object_or_404(EmailSpecification, pk=template_pk)

    if template_instance.template_context == 'user':
        selector_class = UserSelectorForm
    else:
        selector_class = AttendeeSelectorForm

    instance = None

    if request.method == 'POST':
        form = selector_class(request.POST)

        if form.is_valid():
            instance = form.get_instance()

    else:
        form = selector_class()

    if instance is None:
        email = template_instance.render_dummy()
    elif template_instance.template_context == 'user':
        email = template_instance.render_user(instance)
    else:
        email = template_instance.render_attendee(instance)

    return render(request,
                  'sadmin2/emails/template_preview.html',
                  {
                      'sadmin2_menu_main_active': 'emails',
                      'sadmin2_breadcrumbs_active': 'emails_template_preview',
                      'sadmin2_menu_tab': menu.sadmin2_menu_tab_template,
                      'sadmin2_menu_tab_active': 'preview',

                      'template': template_instance,
                      'email': email,

                      'form': form
                  })


@sadmin_prerequisites
def template_send(request, template_pk):

    template_instance = get_object_or_404(EmailSpecification, pk=template_pk)

    if template_instance.template_context == 'user':
        selector_class = UserSelectorForm
    else:
        selector_class = AttendeeSelectorForm

    if request.method == 'POST':
        form = selector_class(request.POST)

        if form.is_valid():
            instance = form.get_instance()

            if template_instance.template_context == 'user':
                template_instance.send_email_user(instance, 'sadmin2.emails.send')
            else:
                template_instance.send_email_attendee(instance, 'sadmin2.emails.send')

            messages.success(request, _('E-mail sent'))
            return HttpResponseRedirect(reverse('sadmin2:emails_template_send', kwargs={'template_pk': template_instance.pk}))

    else:
        form = selector_class()

    return render(request,
                  'sadmin2/generic/form.html',
                  {
                      'sadmin2_menu_main_active': 'emails',
                      'sadmin2_breadcrumbs_active': 'emails_template_send',
                      'sadmin2_menu_tab': menu.sadmin2_menu_tab_template,
                      'sadmin2_menu_tab_active': 'send',

                      'template': template_instance,

                      'form': form
                  })

@sadmin_prerequisites
def templates_create(request):

    context = {
        'sadmin2_menu_main_active': 'emails',
        'sadmin2_breadcrumbs_active': 'emails_templates_create',
        'sadmin2_menu_tab': menu.sadmin2_menu_tab_emails,
        'sadmin2_menu_tab_active': 'templates'
    }

    return generic_create_view(request,
                               TemplateForm,
                               reverse('sadmin2:emails_templates'),
                               message_success=_('Template created'),
                               context=context)

