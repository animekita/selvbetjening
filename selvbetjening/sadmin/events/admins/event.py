import datetime
import time

from django.utils.translation import ugettext as _
from django.db.models import Count
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.admin.helpers import AdminForm
from django.views.defaults import RequestContext
from django.core.urlresolvers import reverse
from django.forms.formsets import formset_factory
from django.conf import settings

from selvbetjening.core.members.models import UserLocation

from selvbetjening.core.events.models import Event, AttendState,\
     payment_registered_source, Attend, Payment

from selvbetjening.sadmin.base import admin_formize_set, graph
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
        return '<a href="%s">%s</a>' % (reverse('sadmin:events_attend_changelist', args=[event.pk]),
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

        self.page_map = LeafSPage(_(u'Map'),
                                  'sadmin:%s_%s_map' % self._url_info,
                                  parent=self.page_change)

        self.page_financials = LeafSPage(_(u'Financials'),
                                         'sadmin:%s_%s_financials' % self._url_info,
                                         parent=self.page_change)

        self.object_menu.register(self.page_change, title=self.Meta.display_name)
        self.object_menu.register(self.page_statistics)
        self.object_menu.register(self.page_map)
        self.object_menu.register(self.page_financials)

    def get_urls(self):
        from django.conf.urls import patterns, url, include

        self.attendee_admin = AttendeeAdmin()
        self.attendee_admin.page_root.parent = self.page_change
        self.attendee_admin.module_menu = self.module_menu
        self.attendee_admin.sadmin_menu = self.object_menu
        self.object_menu.register(self.attendee_admin.page_root)

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
            url(r'^(?P<bind_pk>[0-9]+)/map/$',
                self._wrap_view(self.map_view),
                name='%s_%s_map' % self._url_info),
            url(r'^([0-9]+)/financial/$',
                self._wrap_view(self.financial_report_view),
                name='%s_%s_financials' % self._url_info),
            (r'^(?P<bind_pk>[0-9]+)/attendees/', include(self.attendee_admin.urls)),
            (r'^(?P<bind_pk>[0-9]+)/optiongroups/', include(option_group_admin.urls)),
        ) + urlpatterns

        return urlpatterns

    def register_payment_view(self, request):

        number = getattr(settings, 'SADMIN_EVENT_PAYMENTREGISTRATION_FORMS', 1)
        payments = []
        
        RegisterPaymentFormSet = formset_factory(RegisterPaymentForm, extra=number)

        if request.method == 'POST':
            forms = RegisterPaymentFormSet(request.POST)

            if forms.is_valid():
                
                for result in [result for result in forms.cleaned_data if len(result) > 0]:
                    
                    payment = Payment.objects.create(invoice=result['attendee'].invoice,
                                                     amount=result['payment'],
                                                     signee=request.user)

                    payment_registered_source.trigger(result['attendee'].user,
                                                      attendee=result['attendee'],
                                                      payment=payment)
                    
                    payments.append({'attendee': result['attendee'], 
                                     'payment': payment})

                
                forms = RegisterPaymentFormSet()

        else:
            forms = RegisterPaymentFormSet()

        adminforms = admin_formize_set(forms)

        return render_to_response('sadmin/events/register_payment.html',
                                  {'adminforms': adminforms,
                                   'payments': payments,
                                   'current_page': self.page_register_payment,
                                   'menu': self.module_menu},
                                  context_instance=RequestContext(request))

    def statistics_view(self, request, event_pk):
        event = get_object_or_404(Event, pk=event_pk)
        statistics = {}

        # attendees
        attendees = Attend.objects.all().select_related().filter(event=event_pk).prefetch_related('user__attend_set')
        attendees_count = attendees.count()

        def attendee_statistics(state, identifier):
            _attendees = attendees.filter(state=state)
            _count = _attendees.count()

            new = 0
            for attendee in _attendees:
                if attendee.is_new:
                    new += 1

            statistics[identifier + '_count'] = _count
            statistics[identifier + '_new'] = new

            return new

        new_count = attendee_statistics(AttendState.waiting, 'waiting')
        new_count += attendee_statistics(AttendState.accepted, 'accepted')
        new_count += attendee_statistics(AttendState.attended, 'attended')

        # check-in graph

        _attendees = attendees.filter(state=AttendState.attended)\
            .filter(changed__gt=event.startdate)\
            .filter(changed__lt=event.startdate + datetime.timedelta(days=1))

        start = None
        end = None

        for attendee in _attendees:
            if start is None or attendee.changed < start:
                start = attendee.changed

            if end is None or attendee.changed > end:
                end = attendee.changed

        if start is not None:

            normalized_start_unix = time.mktime(datetime.datetime(start.year, start.month, start.day, start.hour).timetuple())
            end_unix = time.mktime(end.timetuple())

            slot_size = (60 * 10)  # 10 minute slots

            def get_slot(time_unix):
                return int((time_unix - normalized_start_unix) / slot_size)

            slots = get_slot(end_unix) + 1

            checkin_times = [0] * slots

            for attendee in _attendees:
                slot = get_slot(time.mktime(attendee.changed.timetuple()))
                checkin_times[slot] += 1

            checkin_axis = [''] * (slots + 1)

            for i in xrange(0, int(slots / 6) + 1):
                slot_time = datetime.datetime(start.year, start.month, start.day, start.hour) + datetime.timedelta(hours=i)
                checkin_axis[i * 6] = slot_time.strftime("%H:%M %x")

            statistics['checkin_axis'] = checkin_axis
            statistics['checkin_times'] = checkin_times

        else:
            statistics['checkin_axis'] = None
            statistics['checkin_times'] = None

        # attendees graph

        _attendees = attendees.filter(registration_date__isnull=False)

        if _attendees.count() > 0:

            first = _attendees.order_by('registration_date')[0].registration_date
            last = _attendees.order_by('-registration_date')[0].registration_date

            try:
                last_changed = _attendees.exclude(state=AttendState.waiting).order_by('-change_timestamp')[0].change_timestamp

                if last_changed > last:
                    last = last_changed
            except IndexError:
                pass

            axis = graph.generate_week_axis(first, last)
            registration_data = [0] * len(axis)
            accepted_data = [0] * len(axis)

            for attendee in _attendees:
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

        invoices = Invoice.objects.select_related().\
                        prefetch_related('payment_set').\
                        prefetch_related('line_set').\
                        filter(attend__in=event.attendees)

        for invoice in invoices:
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

        invoice_queryset = Invoice.objects.select_related().\
            prefetch_related('payment_set').\
            prefetch_related('line_set').\
            filter(attend__event=event)

        if request.method == 'POST' or 'event' in request.GET:
            formattingform = InvoiceFormattingForm(request.REQUEST, invoices=invoice_queryset)
            formattingform.is_valid()
        else:
            formattingform = InvoiceFormattingForm(invoices=invoice_queryset)

        line_groups, total, detailed_view = formattingform.format()

        adminformattingform = AdminForm(formattingform,
                                        [(_('Formatting'), {'fields': formattingform.base_fields.keys()})],
                                        {})

        return render_to_response('sadmin/events/event/financial.html',
                                  {'invoices': invoice_queryset,
                                   'line_groups': line_groups,
                                   'total': total,
                                   'detailed_view': detailed_view,
                                   'adminformattingform': adminformattingform,
                                   'original': event,
                                   'menu': self.module_menu,
                                   'object_menu': self.object_menu,
                                   'current_page': self.page_financials },
                                  context_instance=RequestContext(request))

    def map_view(self, request, bind_pk):
        event = get_object_or_404(Event, pk=bind_pk)

        locations = UserLocation.objects.exclude(lat=None, lng=None).exclude(expired=True).filter(user__attend__event=event.pk).select_related()
        expired = UserLocation.objects.filter(expired=True).count()
        invalid = UserLocation.objects.filter(expired=False).count() - locations.count()

        map_key = getattr(settings, 'MAP_KEY', None)

        return render_to_response('sadmin/members/map.html',
                                  {'menu': self.module_menu,
                                   'current_page': self.page_map,
                                   'locations': locations,
                                   'expired': expired,
                                   'invalid': invalid,
                                   'map_key': map_key,
                                   'original' : event,
                                   'menu': self.module_menu,
                                   'object_menu' : self.object_menu,
                                   'current_page' : self.page_map },
                                  context_instance=RequestContext(request))