from django.utils.translation import ugettext as _
from django.db.models import Count
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.admin.helpers import AdminForm
from django.views.defaults import RequestContext
from django.core.urlresolvers import reverse

from selvbetjening.core.events.models import Event, AttendState,\
     payment_registered_source, Attend
from selvbetjening.core.invoice.models import Invoice, Payment

from selvbetjening.sadmin.base import admin_formize, graph
from selvbetjening.sadmin.base.sadmin import SModelAdmin, main_menu
from selvbetjening.sadmin.base.admin import TranslationInline
from selvbetjening.sadmin.base.nav import SPage, LeafSPage

from selvbetjening.sadmin.events.admins.attendee import AttendeeAdmin
from selvbetjening.sadmin.events.admins.optiongroup import OptionGroupAdmin
from selvbetjening.sadmin.events.admins.group import GroupAdmin
from selvbetjening.sadmin.events.forms import InvoiceFormattingForm, RegisterPaymentForm

class EventAdmin(SModelAdmin):
    class Meta:
        app_name = 'events'
        name = 'event'
        display_name = 'Event'
        display_name_plural = 'Events'
        model = Event

    def attendees_count(event):
        return '<a href="%s">%s</a>' % (reverse('sadmin:events_attendee_changelist', args=[event.pk]),
                                        event.attendees.count())
    attendees_count.short_description = 'Attendees'
    attendees_count.admin_order_field = 'attend__count'
    attendees_count.allow_tags = True

    list_display = ('title', attendees_count, 'startdate',)
    list_filter = ('registration_open',)
    search_fields = ('title',)

    inlines = [TranslationInline]

    fieldsets = (
        (None, {
            'fields' : ('title', 'description', 'group', 'startdate', 'enddate', 'registration_open'),
            }),
        (_('Conditions'), {
            'fields' : ('maximum_attendees', 'move_to_accepted_policy', ),
            'classes' : ('collapse', ),
            }),
        (_('Custom signup message'), {
            'fields' : ('show_custom_signup_message', 'custom_signup_message'),
            'classes' : ('collapse', ),
            }),
        (_('Custom change message'), {
            'fields' : ('show_custom_change_message', 'custom_change_message'),
            'classes' : ('collapse', ),
            }),
        (_('Custom status page'), {
            'fields' : ('show_custom_status_page', 'custom_status_page'),
            'classes' : ('collapse', ),
            }),
    )

    def queryset(self, request):
        qs = super(EventAdmin, self).queryset(request)

        return qs.distinct().annotate(Count('attend'))

    def _init_navigation(self):
        super(EventAdmin, self)._init_navigation()

        main_menu.register(self.page_root)

        self.page_register_payment = SPage(_(u'Register Payment'),
                                           'sadmin:%s_%s_register_payment' % self._url_info,
                                           parent=self.page_root)

        self.module_menu.register(self.page_register_payment)

        self.page_statistics = LeafSPage(_(u'Statistics'),
                                         'sadmin:%s_%s_statistics' % self._url_info,
                                         parent=self.page_change)

        self.page_financials = LeafSPage(_(u'Financials'),
                                         'sadmin:%s_%s_financials' % self._url_info,
                                         parent=self.page_change)

        self.object_menu.register(self.page_change, title=self.Meta.display_name)
        self.object_menu.register(self.page_statistics)
        self.object_menu.register(self.page_financials)

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url, include

        attendee_admin = AttendeeAdmin()
        attendee_admin.page_root.parent = self.page_change
        attendee_admin.module_menu = self.module_menu
        attendee_admin.sadmin_menu = self.object_menu
        self.object_menu.register(attendee_admin.page_root)

        option_group_admin = OptionGroupAdmin()
        option_group_admin.page_root.parent = self.page_change
        option_group_admin.module_menu = self.module_menu
        option_group_admin.sadmin_menu = self.object_menu
        self.object_menu.register(option_group_admin.page_root)

        group_admin = GroupAdmin()
        group_admin.page_root.parent = self.page_root
        group_admin.module_menu = self.module_menu
        self.module_menu.register(group_admin.page_root)

        urlpatterns = super(EventAdmin, self).get_urls()

        urlpatterns = patterns('',
            url(r'^register-payment/$',
                self._wrap_view(self.register_payment_view),
                name='%s_%s_register_payment' % self._url_info),
            (r'^groups/', include(group_admin.urls)),
            url(r'^([0-9]+)/statistics/$',
                self._wrap_view(self.statistics_view),
                name='%s_%s_statistics' % self._url_info),
            url(r'^([0-9]+)/financial/$',
                self._wrap_view(self.financial_report_view),
                name='%s_%s_financials' % self._url_info),
            (r'^(?P<bind_pk>[0-9]+)/attendees/', include(attendee_admin.urls)),
            (r'^(?P<bind_pk>[0-9]+)/optiongroups/', include(option_group_admin.urls)),
        ) + urlpatterns

        return urlpatterns

    def register_payment_view(self, request):
        found_attendee = None
        payment = None
        multiple_attendees = None

        if request.method == 'POST':
            form = RegisterPaymentForm(request.POST)

            if form.is_valid():
                if len(form.attendees) == 1:
                    handler, found_attendee = form.attendees[0]
                    payment = Payment.objects.create(invoice=found_attendee.invoice,
                                                     amount=form.cleaned_data['payment'],
                                                     signee=request.user)

                    payment_registered_source.trigger(found_attendee.user,
                                                      attendee=found_attendee,
                                                      payment=payment)

                    form = RegisterPaymentForm()

                else:
                    multiple_attendees = form.attendees

        else:
            form = RegisterPaymentForm()

        adminform = admin_formize(form)

        return render_to_response('sadmin/events/register_payment.html',
                                  {'adminform': adminform,
                                   'found_attendee': found_attendee,
                                   'payment': payment,
                                   'multiple_attendees': multiple_attendees,
                                   'current_page': self.page_register_payment,
                                   'menu': self.module_menu},
                                  context_instance=RequestContext(request))

    def statistics_view(self, request, event_pk):
        event = get_object_or_404(Event, pk=event_pk)
        statistics = {}

        # attendees
        attendees_count = event.attendees.count()

        def attendee_statistics(state, identifier):
            attendees = event.attendees.filter(state=state)
            count = attendees.count()

            new = 0
            for attendee in attendees:
                if attendee.is_new():
                    new += 1

            statistics[identifier + '_count'] = count
            statistics[identifier + '_new'] = new

            return new

        new_count = attendee_statistics(AttendState.waiting, 'waiting')
        new_count += attendee_statistics(AttendState.accepted, 'accepted')
        new_count += attendee_statistics(AttendState.attended, 'attended')

        # attendees graph

        attendees = event.attendees.filter(registration_date__isnull=False)

        if attendees.count() > 0:

            first = attendees.order_by('registration_date')[0].registration_date
            last = attendees.order_by('-registration_date')[0].registration_date

            try:
                last_changed = attendees.exclude(state=AttendState.waiting).order_by('-change_timestamp')[0].change_timestamp

                if last_changed > last:
                    last = last_changed
            except Attend.DoesNotExist:
                pass

            axis = graph.generate_week_axis(first, last)
            registration_data = [0 for i in axis]
            accepted_data = [0 for i in axis]

            for attendee in attendees:
                week = graph.diff_in_weeks(first, attendee.registration_date)
                registration_data[week] += 1

                if attendee.state != AttendState.waiting:
                    week = graph.diff_in_weeks(first, attendee.change_timestamp)
                    accepted_data[week] += 1

            statistics['registrations_data'] = graph.insert_prefix(registration_data)
            statistics['registrations_data_acc'] = graph.accumulate(registration_data)
            statistics['accepted_data'] = graph.insert_prefix(accepted_data)
            statistics['accepted_data_acc'] = graph.accumulate(accepted_data)
            statistics['registrations_axis'] = graph.insert_prefix(axis, axis=True)

        # invoices
        statistics['invoice_payment_total'] = 0
        statistics['invoice_paid'] = 0

        statistics['invoices_in_balance'] = 0
        statistics['invoices_unpaid'] = 0
        statistics['invoices_partial'] = 0
        statistics['invoices_overpaid'] = 0
        statistics['invoices_count'] = 0

        for invoice in Invoice.objects.filter(attend__in=event.attendees):
            statistics['invoices_count'] += 1

            if invoice.in_balance():
                statistics['invoices_in_balance'] += 1

            if invoice.is_unpaid():
                statistics['invoices_unpaid'] += 1

            if invoice.is_overpaid():
                statistics['invoices_overpaid'] += 1

            if invoice.is_partial():
                statistics['invoices_partial'] += 1

            statistics['invoice_payment_total'] += invoice.total_price
            statistics['invoice_paid'] += invoice.paid

        # tilvalg

        optiongroups = []
        for optiongroup in event.optiongroup_set.all():
            options = []
            for option in optiongroup.option_set.all():
                count = option.selections.count()
                waiting = option.selections.filter(attendee__state=AttendState.waiting).count()
                accepted = option.selections.filter(attendee__state=AttendState.accepted).count()
                attended = option.selections.filter(attendee__state=AttendState.attended).count()
                options.append((option, count, waiting, accepted, attended))

            optiongroups.append((optiongroup, options))

        statistics.update({'menu': self.module_menu,
                           'object_menu': self.object_menu,
                           'current_page': self.page_statistics,
                           'original' : event,
                           'attendees_count' : attendees_count,
                           'new_count' : new_count,
                           'optiongroups' : optiongroups,})

        return render_to_response('sadmin/events/event/statistics.html',
                                  statistics,
                                  context_instance=RequestContext(request))

    def financial_report_view(self, request, event_pk):
        event = get_object_or_404(Event, pk=event_pk)
        invoice_queryset = Invoice.objects.filter(attend__event=event)

        if request.method == 'POST' or request.GET.has_key('event'):
            formattingform = InvoiceFormattingForm(request.REQUEST, invoices=invoice_queryset)
            formattingform.is_valid()
        else:
            formattingform = InvoiceFormattingForm(invoices=invoice_queryset)

        line_groups, total = formattingform.format()

        adminformattingform = AdminForm(formattingform,
                                        [(_('Formatting'), {'fields': formattingform.base_fields.keys()})],
                                        {})

        return render_to_response('sadmin/events/event/financial.html',
                                  {'invoices' : invoice_queryset,
                                   'line_groups' : line_groups,
                                   'total' : total,
                                   'adminformattingform' : adminformattingform,
                                   'original' : event,
                                   'menu': self.module_menu,
                                   'object_menu' : self.object_menu,
                                   'current_page' : self.page_financials },
                                  context_instance=RequestContext(request))