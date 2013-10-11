from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _

from mailqueue.models import MailerMessage

from selvbetjening.core.mailcenter.models import EmailSpecification

from selvbetjening.sadmin2.views.generic import search_view, generic_create_view
from selvbetjening.sadmin2 import menu
from selvbetjening.sadmin2.decorators import sadmin_prerequisites
from selvbetjening.sadmin2.forms import TemplateForm


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

        'template': instance
    }

    return generic_create_view(request,
                               TemplateForm,
                               reverse('sadmin2:emails_template', kwargs={'template_pk': instance.pk}),
                               message_success=_('Template saved'),
                               context=context,
                               instance=instance)


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