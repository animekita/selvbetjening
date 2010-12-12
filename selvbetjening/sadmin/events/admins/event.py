from django.utils.translation import ugettext as _
from django.db.models import Count
from django.shortcuts import render_to_response, get_object_or_404

from selvbetjening.core.translation.admin import TranslationInline
from selvbetjening.core.events.models import Event, AttendState, AttendState
from selvbetjening.core.invoice.models import Invoice

from selvbetjening.sadmin.events import nav
from selvbetjening.sadmin.events.admins.attendee import AttendeeAdmin
from selvbetjening.sadmin.events.admins.optiongroup import OptionGroupAdmin
from selvbetjening.sadmin.base.sadmin import SAdminContext, SModelAdmin

class EventAdmin(SModelAdmin):
    class Meta:
        app_name = 'events'
        name = 'event'
        model = Event

    def attendees_count(event):
        return event.attendees.count()
    attendees_count.short_description = 'Attendees'
    attendees_count.admin_order_field = 'attend__count'

    list_display = ('title', attendees_count, 'startdate',)
    list_filter = ('registration_open',)
    search_fields = ('title',)

    inlines = [TranslationInline]

    fieldsets = (
        (None, {
            'fields' : ('title', 'description', 'startdate', 'enddate', 'registration_open'),
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

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url, include

        urlpatterns = super(EventAdmin, self).get_urls()

        urlpatterns = patterns('',
            url(r'^(?P<event_pk>[0-9]+)/statistics/$',
                self._wrap_view(self.statistics_view),
                name='%s_%s_statistic' % self._url_info),
            (r'^(?P<bind_pk>[0-9]+)/attendees/', include(AttendeeAdmin().urls)),
            (r'^(?P<bind_pk>[0-9]+)/optiongroups/', include(OptionGroupAdmin().urls)),
        ) + urlpatterns

        return urlpatterns

    def change_view(self, request, object_id, extra_context=None):
        extra_context = extra_context or {}
        extra_context['menu'] = nav.event_menu.render(event_pk=object_id)
        return super(EventAdmin, self).change_view(request, object_id, extra_context)

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

        statistics.update({'menu': nav.event_menu.render(event_pk=event.pk),
                           'original' : event,
                           'attendees_count' : attendees_count,
                           'new_count' : new_count,
                           'optiongroups' : optiongroups,})

        return render_to_response('sadmin/events/event/statistics.html',
                                  statistics,
                                  context_instance=SAdminContext(request))
