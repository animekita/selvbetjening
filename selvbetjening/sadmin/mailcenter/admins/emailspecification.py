from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User

from selvbetjening.core.mailcenter.models import EmailSpecification
from selvbetjening.core.forms import form_collection_builder
from selvbetjening.core.mailcenter.models import EmailSpecification

from selvbetjening.sadmin.base import admin_formize
from selvbetjening.sadmin.base.sadmin import SAdminContext, SModelAdmin

from selvbetjening.sadmin.mailcenter.forms import SendEmailForm, SendNewsletterForm, conditionform_registry
from selvbetjening.sadmin.mailcenter.admins.outgoing import OutgoingAdmin
from selvbetjening.sadmin.mailcenter import nav

class EmailSpecificationAdmin(SModelAdmin):
    class Meta:
        app_name = 'mailcenter'
        name = 'emailspecification'
        model = EmailSpecification

    list_display = ('subject',)
    search_fields = ('subject', 'body')

    fieldsets = (
        (None, {
            'fields': ('subject', 'body'),
            }),
        (_(u'Recipient'), {
            'fields': ('send_to_user', 'other_recipients')
            }),
        (_(u'Source'), {
            'fields': (('source_enabled', 'event'),),
            'description': _(u"""
            <p>You can bind an e-mail to an event in Selvbetjening, sending the bound e-mail
            each time the event is triggered. The recipient of this e-mail is the user for
            which the event concerns.</p>

            <p>E.g. the <i>"user registered for event"</i> event is triggered when a user registers
            for the event, and a bound e-mail would be send to that given user.</p>

            <p>Depending on the bound event, additional parameters are made available for the e-mail template. A user parameter, representing the receiver, is always present. Furthermore, bound e-mails can't be send as mass e-mail.</p>
            """)
            }),
    )

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url, include

        urlpatterns = super(EmailSpecificationAdmin, self).get_urls()

        urlpatterns = patterns('',
            url(r'^(?P<email_pk>[0-9]+)/filter/$',
                self._wrap_view(self.filter_view),
                name='%s_%s_change_filter' % self._url_info),
            url(r'^(?P<email_pk>[0-9]+)/send/$',
                self._wrap_view(self.send_view),
                name='%s_%s_send' % self._url_info),
            url(r'^(?P<email_pk>[0-9]+)/mass-send/$',
                self._wrap_view(self.masssend_view),
                name='%s_%s_masssend' % self._url_info),
            (r'^outgoing/', include(OutgoingAdmin().urls)),
        ) + urlpatterns

        return urlpatterns

    def add_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['menu'] = nav.emails_menu.render()
        return super(EmailSpecificationAdmin, self).add_view(request, extra_context=extra_context)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['menu'] = nav.emails_menu.render()
        extra_context['title'] = _(u'Browse E-mail Specifications')
        return super(EmailSpecificationAdmin, self).changelist_view(request, extra_context)

    def change_view(self, request, object_id, extra_context=None):
        extra_context = extra_context or {}
        extra_context['menu'] = nav.email_menu.render(email_pk=object_id)
        return super(EmailSpecificationAdmin, self).change_view(request, object_id, extra_context)

    def filter_view(self, request, email_pk):
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

        menu = nav.email_menu.render(email_pk=email.pk)

        return render_to_response('sadmin/mailcenter/email/filter.html',
                                  {'email': email,
                                   'forms': [admin_formize(form) for form in forms],
                                   'menu': menu},
                                  context_instance=SAdminContext(request))


    def masssend_view(self, request, email_pk):
        email = get_object_or_404(EmailSpecification, pk=email_pk)
        menu = nav.email_menu.render(email_pk=email.pk)

        if len(email.event) > 0:
            # can't send newsletter when bound to event
            return render_to_response('sadmin/mailcenter/email/email-bound.html',
                                      {'email': email,
                                       'menu': menu},
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

        return render_to_response('sadmin/mailcenter/email/massemail.html',
                                  {'form': admin_formize(form),
                                   'email': email,
                                   'recipients': recipients,
                                   'menu': menu},
                                  context_instance=SAdminContext(request))

    def send_view(self, request, email_pk):
        email = get_object_or_404(EmailSpecification, pk=email_pk)

        if request.method == 'POST':
            form = SendEmailForm(request.POST)

            if form.is_valid():
                user = form.cleaned_data['user']

                email.send_email(user, bypass_conditions=True)
                messages.success(request, _(u'E-mail successfully sent to %s') % user.get_full_name())

                form = SendEmailForm()

        else:
            form = SendEmailForm()

        menu = nav.email_menu.render(email_pk=email.pk)

        return render_to_response('sadmin/mailcenter/email/send.html',
                                  {'form': admin_formize(form),
                                   'email': email,
                                   'menu': menu},
                                  context_instance=SAdminContext(request))