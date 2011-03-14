# -- encoding: utf-8 --

from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib import messages
from django.core.urlresolvers import reverse

from selvbetjening.core.events.models import Event, Attend, AttendState, \
     request_attendee_pks_signal
from selvbetjening.core.events.processor_handlers import change_selection_processors, checkin_processors
from selvbetjening.core.events.forms import OptionForms
from selvbetjening.core.invoice.models import Payment
from selvbetjening.core.forms import form_collection_builder

from selvbetjening.sadmin.base.sadmin import SBoundModelAdmin, SAdminContext, site
from selvbetjening.sadmin.base.nav import LeafSPage, RemoteSPage
from selvbetjening.sadmin.base import admin_formize

from selvbetjening.sadmin.events import nav
from selvbetjening.sadmin.events.admins.nonattendee import NonAttendeeAdmin
from selvbetjening.sadmin.events.forms import PaymentForm

class AttendeeAdmin(SBoundModelAdmin):
    class Meta:
        app_name = 'events'
        name = 'attendee'
        display_name = 'Attendee'
        display_name_plural = 'Attendees'
        model = Attend
        bound_model = Event
        default_views = ('list', 'delete', 'change')

    def name(attendee):
        user = attendee.user
        return u'%s %s' % (user.first_name, user.last_name)
    name.short_description = _('Name')

    def in_balance(attendee):
        if attendee.invoice.in_balance():
            return '<span class="attr success">%s</span>' % _('Betalt')
        elif attendee.invoice.is_overpaid():
            return '<span class="attr warning">%s</span>' % _('Overpaid')
        elif attendee.invoice.is_partial():
            return '<span class="attr warning">%s</span>' % _('Underpaid')
        return '<span class="attr error">%s</span>' % _('Unpaid')
    in_balance.short_description = _('Payment')
    in_balance.allow_tags = True

    def status(attendee):
        status_map = {AttendState.attended : 'success',
                      AttendState.waiting : 'error',
                      AttendState.accepted : 'warning',}

        return '<span class="attr %s">%s</span>' % (status_map[attendee.state],
                                                    attendee.get_state_display())
    status.allow_tags = True


    def attendee_actions(attendee):
        if attendee.state == AttendState.attended:
            return ''
        else:
            checkin_url = reverse('sadmin:events_attendee_checkin', args=[attendee.event.pk, attendee.pk])
            return '<b><a class="iframe" href="%s?_popup=1&_modal=1">check-in</a></b>' % checkin_url

    attendee_actions.allow_tags = True
    attendee_actions.short_description = ''

    list_filter = ('state',)
    list_per_page = 50
    list_display = ('user', name, status, in_balance, attendee_actions)

    search_fields = ('user__username', 'user__first_name', 'user__last_name')

    def _init_navigation(self):
        super(AttendeeAdmin, self)._init_navigation()

        self.page_payment_keys = LeafSPage(_(u'Payment Keys'),
                                           'sadmin:%s_%s_payment_keys' % self._url_info,
                                           parent=self.page_change,
                                           depth=self.depth)

        self.page_selections = LeafSPage(_(u'Selections'),
                                         'sadmin:%s_%s_selections' % self._url_info,
                                         parent=self.page_change,
                                         depth=self.depth)

        self.object_menu.register(self.page_change, title=self.Meta.display_name)
        self.object_menu.register(self.page_payment_keys)
        self.object_menu.register(self.page_selections)

        profile_url = lambda context, stack: reverse('sadmin:auth_user_change', args=[stack[-1].user.pk])
        self.page_profile = RemoteSPage(_(u'User Information'), profile_url)

        self.related_objects_menu.register(self.page_profile)

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url, include

        urlpatterns = super(AttendeeAdmin, self).get_urls()

        non_attendee_admin = NonAttendeeAdmin()
        non_attendee_admin.page_root.parent = self.page_root
        non_attendee_admin.sadmin_menu = self.sadmin_menu
        non_attendee_admin.sadmin_action_menu = self.sadmin_action_menu
        self.sadmin_action_menu.register(non_attendee_admin.page_root,
                                         title=_('Add Attendee'))

        urlpatterns = patterns('',
            url(r'^([0-9]+)/selections/',
                self._wrap_view(self.selections_view),
                name='%s_%s_selections' % self._url_info),
            url(r'^([0-9]+)/pks/$',
                self._wrap_view(self.payment_keys_view),
                name='%s_%s_payment_keys' % self._url_info),
            url(r'^([0-9]+)/checkin/$',
                self._wrap_view(self.checkin_view),
                name='%s_%s_checkin' % self._url_info),
            (r'^new/', include(non_attendee_admin.urls)),
            ) + urlpatterns

        return urlpatterns

    def queryset(self, request):
        qs = super(SBoundModelAdmin, self).queryset(request)

        return qs.filter(event=request.bound_object)

    def change_view(self, request, attendee_pk, extra_context=None):
        attendee = get_object_or_404(Attend, pk=attendee_pk)

        if request.method == 'POST' and not request.POST.has_key('do_single_payment'):
            if request.POST.has_key('do_accept'):
                attendee.state = AttendState.accepted
                attendee.save()

                messages.success(request, _(u'Attendee moved to the accepted list'))

            elif request.POST.has_key('do_unaccept'):
                attendee.state = AttendState.waiting
                attendee.save()

                messages.success(request, _(u'Attendee moved back to the waiting list'))

            elif request.POST.has_key('do_checkin'):
                attendee.state = AttendState.attended
                attendee.save()

                messages.success(request, _(u'Attendee checked-in'))

            elif request.POST.has_key('do_checkout'):
                attendee.state = AttendState.accepted
                attendee.save()

                messages.success(request, _(u'Attendee checked-out'))

            elif request.POST.has_key('do_checkin_and_pay'):
                attendee.state = AttendState.attended
                attendee.save()

                Payment.objects.create(invoice=attendee.invoice,
                                       amount=attendee.invoice.unpaid,
                                       signee=request.user)

                messages.success(request, _(u'Attendee checked-in and paied for'))

            elif request.POST.has_key('do_pay'):
                Payment.objects.create(invoice=attendee.invoice,
                                       amount=attendee.invoice.unpaid,
                                       signee=request.user)

                messages.success(request, _(u'Attendee paied for'))

            form = PaymentForm()

        elif request.method == 'POST' and request.POST.has_key('do_single_payment'):
            form = PaymentForm(request.POST)
            form.invoice = attendee.invoice

            if form.is_valid():
                payment = form.save(commit=False)
                payment.invoice = attendee.invoice
                payment.signee = request.user
                payment.save()

                messages.success(request, _(u'Payment registered'))

                form = PaymentForm()
        else:
            form = PaymentForm()

        context = {'menu': self.object_menu,
                   'action_menu': self.object_action_menu,
                   'related_objects_menu': self.related_objects_menu,
                   'current_page': self.page_change,
                   'attendee': attendee,
                   'original': attendee,
                   'form': admin_formize(form),
                   'is_popup': request.REQUEST.has_key('_popup')}

        context.update(extra_context or {})

        return render_to_response('sadmin/events/attendee/change.html',
                                  context,
                                  context_instance=SAdminContext(request))

    def selections_view(self, request, attendee_id, extra_context=None):
        attendee = get_object_or_404(Attend, event=request.bound_object, pk=attendee_id)

        change_selection_handler = change_selection_processors.get_handler(request, attendee)

        if request.method == 'POST' and request.POST.get('submit_option', False):
            option_forms = OptionForms(attendee.event, request.POST, attendee=attendee)

            if change_selection_handler.is_valid() and option_forms.is_valid():
                change_selection_handler.save()
                option_forms.save()

                messages.success(request, _(u'Selections changed'))

        else:
            option_forms = OptionForms(attendee.event, attendee=attendee)

        checkin_parts = change_selection_handler.view()

        context = {'menu': self.object_menu,
                   'current_page': self.page_selections,
                   'original': attendee,
                   'option_forms' : option_forms,
                   'checkin_parts' : checkin_parts}

        context.update(extra_context or {})

        return render_to_response('sadmin/events/attendee/selections.html',
                                  context,
                                  context_instance=SAdminContext(request))

    def payment_keys_view(self, request, attendee_pk, extra_context=None):
        attendee = get_object_or_404(Attend, pk=attendee_pk)

        pks = request_attendee_pks_signal.send(self, attendee=attendee)

        context = {'menu': self.object_menu,
                   'current_page' : self.page_payment_keys,
                   'original': attendee,
                   'pks': pks}

        context.update(extra_context or {})

        return render_to_response('sadmin/events/attendee/show_pks.html',
                                  context,
                                  context_instance=SAdminContext(request))

    def checkin_view(self, request, attendee_pk, extra_context=None):
        attendee = get_object_or_404(Attend, pk=attendee_pk)

        if request.method == 'POST':
            if request.POST.has_key('do_checkin'):
                attendee.state = AttendState.attended
                attendee.save()

            elif request.POST.has_key('do_payment'):
                Payment.objects.create(invoice=attendee.invoice,
                                       amount=attendee.invoice.unpaid,
                                       signee=request.user)

        context = {'original': attendee,
                   'is_popup': request.REQUEST.has_key('_popup'),
                   'is_modal': request.REQUEST.has_key('_modal')}
        context.update(extra_context)

        return render_to_response('sadmin/events/attendee/checkin.html',
                                  context,
                                  context_instance=SAdminContext(request))