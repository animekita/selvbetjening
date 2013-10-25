
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.views.decorators.http import require_POST

from mailqueue.models import MailerMessage

from selvbetjening.core.user.models import SUser
from selvbetjening.core.events.models import Event, Attend, Option
from selvbetjening.core.mailcenter.models import EmailSpecification

from selvbetjening.sadmin2.views.generic import search_view, generic_create_view
from selvbetjening.sadmin2 import menu
from selvbetjening.sadmin2.decorators import sadmin_prerequisites
from selvbetjening.sadmin2.forms import TemplateForm, UserSelectorForm, AttendeeSelectorForm, AttendeesNewsletterFilter, AttendeesNewsletterFilterHidden


@sadmin_prerequisites
def queue(request):

    queryset = MailerMessage.objects.all().\
        order_by('sent', '-last_attempt', '-pk')

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
def template_newsletter_users(request, template_pk):

    template_instance = get_object_or_404(EmailSpecification, pk=template_pk)

    if template_instance.template_context != 'user':
        return render(request, 'sadmin2/generic/error.html',
                      {
                          'subject': _('Wrong template context:'),
                          'message': _('This template is not using the user template context required by the user newsletter')
                      },
                      status=403)

    users = SUser.objects.filter(send_me_email=True)

    if request.method == 'POST':

        for user in users:
            template_instance.send_email_user(user, 'sadmin2.emails.newsletter.users')

        messages.success(request, _('E-mails queued for dispatch'))
        return HttpResponseRedirect(reverse('sadmin2:emails_template_newsletter_users',
                                            kwargs={'template_pk': template_instance.pk}))

    return render(request,
                  'sadmin2/emails/template_newsletter_users.html',
                  {
                      'sadmin2_menu_main_active': 'emails',
                      'sadmin2_breadcrumbs_active': 'emails_template_newsletter_users',
                      'sadmin2_menu_tab': menu.sadmin2_menu_tab_template,
                      'sadmin2_menu_tab_active': 'mass_send',

                      'template': template_instance,

                      'user_email_count': users.count()
                  })


@sadmin_prerequisites
def template_newsletter_attendees(request, template_pk):

    template_instance = get_object_or_404(EmailSpecification, pk=template_pk)

    events = Event.objects.all()

    return render(request,
                  'sadmin2/emails/template_newsletter_attendees.html',
                  {
                      'sadmin2_menu_main_active': 'emails',
                      'sadmin2_breadcrumbs_active': 'emails_template_newsletter_attendees',
                      'sadmin2_menu_tab': menu.sadmin2_menu_tab_template,
                      'sadmin2_menu_tab_active': 'mass_send',

                      'template': template_instance,

                      'events': events
                  })


@sadmin_prerequisites
def template_newsletter_attendees_step2(request, template_pk, event_pk):

    template_instance = get_object_or_404(EmailSpecification, pk=template_pk)
    event = get_object_or_404(Event, pk=event_pk)

    form = AttendeesNewsletterFilter(event=event)

    return render(request,
                  'sadmin2/emails/template_newsletter_attendees_step2.html',
                  {
                      'sadmin2_menu_main_active': 'emails',
                      'sadmin2_breadcrumbs_active': 'emails_template_newsletter_attendees',
                      'sadmin2_menu_tab': menu.sadmin2_menu_tab_template,
                      'sadmin2_menu_tab_active': 'mass_send',

                      'template': template_instance,

                      'event': event,

                      'form': form
                  })


@sadmin_prerequisites
@require_POST
def template_newsletter_attendees_step3(request, template_pk, event_pk):

    template_instance = get_object_or_404(EmailSpecification, pk=template_pk)
    event = get_object_or_404(Event, pk=event_pk)

    form = AttendeesNewsletterFilterHidden(request.POST, event=event)
    assert form.is_valid()

    attendees = Attend.objects.filter(event=event)

    if len(form.cleaned_data['status']) > 0:
        attendees = attendees.filter(state__in=form.cleaned_data['status'])

    if len(form.cleaned_data['options']):
        attendees = attendees.filter(selection__option__in=form.cleaned_data['options'])

    attendees = attendees.distinct()

    if request.POST.get('commit', False):  # commit is added by a second post on this page

        for attendee in attendees:
            template_instance.send_email_attendee(attendee, 'sadmin2.emails.newsletter.users')

        messages.success(request, _('%s e-mails queued for dispatch') % len(attendees))
        return HttpResponseRedirect(reverse('sadmin2:emails_template_newsletter_attendees',
                                            kwargs={'template_pk': template_instance.pk}))

    return render(request,
                  'sadmin2/emails/template_newsletter_attendees_step3.html',
                  {
                      'sadmin2_menu_main_active': 'emails',
                      'sadmin2_breadcrumbs_active': 'emails_template_newsletter_attendees',
                      'sadmin2_menu_tab': menu.sadmin2_menu_tab_template,
                      'sadmin2_menu_tab_active': 'mass_send',

                      'template': template_instance,
                      'event': event,

                      'filter_status': form.cleaned_data['status'],
                      'filter_options': Option.objects.filter(pk__in=form.cleaned_data['options']),

                      'attendees_count': attendees.count(),

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

