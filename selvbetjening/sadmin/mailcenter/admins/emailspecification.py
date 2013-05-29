from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.defaults import RequestContext

from selvbetjening.core.mailcenter.models import EmailSpecification

from selvbetjening.sadmin.base import admin_formize
from selvbetjening.sadmin.base.sadmin import SModelAdmin, main_menu
from selvbetjening.sadmin.base.nav import LeafSPage

from selvbetjening.sadmin.mailcenter.forms import SendEmailForm, SendNewsletterForm, conditionform_registry,\
    form_collection_builder
from selvbetjening.sadmin.mailcenter.admins.outgoing import OutgoingAdmin


class EmailSpecificationAdmin(SModelAdmin):
    class Meta:
        app_name = 'mailcenter'
        name = 'emailspecification'
        model = EmailSpecification

        display_name_plural = 'E-mails'
        display_name = 'E-mail'

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

    def _init_navigation(self):
        super(EmailSpecificationAdmin, self)._init_navigation()

        main_menu.register(self.page_root)

        self.page_filter = LeafSPage(_(u'Filters'),
                                     'sadmin:mailcenter_emailspecification_change_filter',
                                     parent=self.page_change,
                                     permission=lambda user: user.has_perm('mailcenter.change_emailspecification'))

        self.page_send = LeafSPage(_(u'Send'),
                                   'sadmin:mailcenter_emailspecification_send',
                                   parent=self.page_change,
                                   permission=lambda user: user.has_perm('mailcenter.change_emailspecification'))

        self.page_mass_email = LeafSPage(_(u'Mass E-email'),
                                         'sadmin:mailcenter_emailspecification_masssend',
                                         parent=self.page_change,
                                         permission=lambda user: user.has_perm('mailcenter.change_emailspecification'))


        self.object_menu.register(self.page_change, title=_('E-mail'))
        self.object_menu.register(self.page_filter)
        self.object_menu.register(self.page_send)
        self.object_menu.register(self.page_mass_email)

    def get_urls(self):
        from django.conf.urls import patterns, url, include

        outgoing_admin = OutgoingAdmin()
        outgoing_admin.page_root.parent = self.page_root
        outgoing_admin.module_menu = self.module_menu
        self.module_menu.register(outgoing_admin.page_root)


        urlpatterns = super(EmailSpecificationAdmin, self).get_urls()

        urlpatterns = patterns('',
            url(r'^([0-9]+)/filter/$',
                self._wrap_view(self.filter_view),
                name='%s_%s_change_filter' % self._url_info),
            url(r'^([0-9]+)/send/$',
                self._wrap_view(self.send_view),
                name='%s_%s_send' % self._url_info),
            url(r'^([0-9]+)/mass-send/$',
                self._wrap_view(self.masssend_view),
                name='%s_%s_masssend' % self._url_info),
            (r'^outgoing/', include(outgoing_admin.urls)),
        ) + urlpatterns

        return urlpatterns

    def change_view(self, request, object_id, extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = _(u'Change E-mail')
        return super(EmailSpecificationAdmin, self).change_view(request, object_id, extra_context=extra_context)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = _(u'Browse E-mails')
        return super(EmailSpecificationAdmin, self).changelist_view(request, extra_context)

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

        return render_to_response('sadmin/mailcenter/email/filter.html',
                                  {'email': email,
                                   'original': email, # compatibility
                                   'forms': [admin_formize(form) for form in forms],
                                   'menu': self.module_menu,
                                   'object_menu': self.object_menu,
                                   'current_page': self.page_filter},
                                  context_instance=RequestContext(request))

    def masssend_view(self, request, email_pk):
        email = get_object_or_404(EmailSpecification, pk=email_pk)

        if len(email.event) > 0:
            # can't send newsletter when bound to event
            return render_to_response('sadmin/mailcenter/email/email-bound.html',
                                      {'email': email,
                                       'original': email, # compatibility
                                       'menu': self.module_menu,
                                       'object_menu': self.object_menu,
                                       'current_page': self.page_mass_email},
                                      context_instance=RequestContext(request))

        recipients = User.objects.filter(userprofile__send_me_email=True)\
            .exclude(username__in=email.recipients.values_list('username', flat=True))

        attend_cache = {}  # populated by demand, yes this is ugly :(

        for condition in email.conditions:
            recipients = [recipient for recipient in recipients if condition.passes(recipient, attend_cache=attend_cache)]

        if request.method == 'POST':
            form = SendNewsletterForm(request.POST)

            if  form.is_valid():
                email.send_email(recipients)
                email.recipients.add(*recipients)
                messages.success(request, _(u'Newsletter sucessfully sent to %s receipients') % len(recipients))

                return HttpResponseRedirect(
                    reverse('sadmin:%s_%s_masssend' % self._url_info, args=[email.pk]))

        else:
            form = SendNewsletterForm()

        return render_to_response('sadmin/mailcenter/email/massemail.html',
                                  {'form': admin_formize(form),
                                   'email': email,
                                   'original': email, # compatibility
                                   'recipients': recipients,
                                   'object_menu': self.object_menu,
                                   'menu': self.module_menu,
                                   'current_page': self.page_mass_email},
                                  context_instance=RequestContext(request))

    def send_view(self, request, email_pk):
        email = get_object_or_404(EmailSpecification, pk=email_pk)

        if request.method == 'POST':
            form = SendEmailForm(request.POST, admin_site=self.admin_site)

            if form.is_valid():
                user = form.cleaned_data['user']

                email.send_email(user, bypass_conditions=True)
                messages.success(request, _(u'E-mail successfully sent to %s') % user.get_full_name())

                form = SendEmailForm(admin_site=self.admin_site)

        else:
            form = SendEmailForm(admin_site=self.admin_site)

        return render_to_response('sadmin/mailcenter/email/send.html',
                                  {'form': admin_formize(form),
                                   'email': email,
                                   'original': email, # compatibility
                                   'menu': self.module_menu,
                                   'object_menu': self.object_menu,
                                   'current_page': self.page_send},
                                  context_instance=RequestContext(request))