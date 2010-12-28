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

from selvbetjening.sadmin.base.sadmin import SBoundModelAdmin, SAdminContext
from selvbetjening.sadmin.base import admin_formize

from selvbetjening.sadmin.events import nav
from selvbetjening.sadmin.events.admins.nonattendee import NonAttendeeAdmin
from selvbetjening.sadmin.events.admins.invoice import InvoiceAdmin
from selvbetjening.sadmin.events.forms import PaymentForm

class AttendeeAdmin(SBoundModelAdmin):
    class Meta:
        app_name = 'events'
        name = 'attendee'
        model = Attend
        bound_model = Event
        default_views = ('list', 'delete')  
        
    def in_balance(attend):
        return attend.invoice.in_balance()
    in_balance.boolean = True

    list_filter = ('state',)
    list_per_page = 50
    list_display = ('user', 'user_first_name', 'user_last_name', 'state', in_balance)

    search_fields = ('user__username', 'user__first_name', 'user__last_name')

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url, include

        urlpatterns = super(AttendeeAdmin, self).get_urls()

        urlpatterns = patterns('',
            url(r'^(.+)/selections/',
                self._wrap_view(self.selections_view),
                name='%s_%s_selections' % self._url_info),
            url(r'^(?P<attendee_pk>[0-9]+)/$',
                self._wrap_view(self.change_view),
                name='%s_%s_change' % self._url_info),
            url(r'^(?P<attendee_pk>[0-9]+)/pks/$',
                self._wrap_view(self.show_pks_view),
                name='%s_%s_show_pks' % self._url_info),
            (r'^(?P<bind_attendee_pk>.+)/invoice/', include(InvoiceAdmin().urls)),
            (r'^new/', include(NonAttendeeAdmin().urls)),
            ) + urlpatterns

        return urlpatterns

    def queryset(self, request):
        qs = super(SBoundModelAdmin, self).queryset(request)

        return qs.filter(event=request.bound_object)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['menu'] = nav.event_menu.render(event_pk=request.bound_object.pk)

        return super(AttendeeAdmin, self).changelist_view(request, extra_context)
    
    def change_view(self, request, attendee_pk):
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
                
        menu = nav.attendee_menu.render(
            event_pk=request.bound_object.pk,
            attendee_pk=attendee_pk,
            user_pk=attendee.user.pk)
        
        return render_to_response('sadmin/events/attendee/change.html',
                                  {'menu': menu,
                                   'attendee': attendee,
                                   'form': admin_formize(form)},
                                  context_instance=SAdminContext(request))    
    
    def selections_view(self, request, attendee_id):
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

        menu = nav.attendee_menu.render(event_pk=request.bound_object.pk,
                                        attendee_pk=attendee_id,
                                        user_pk=attendee.user.pk)

        return render_to_response('sadmin/events/attendee/selections.html',
                                  {'menu': menu,
                                   'attendee': attendee,
                                   'option_forms' : option_forms,
                                   'checkin_parts' : checkin_parts},
                                  context_instance=SAdminContext(request))

    def show_pks_view(self, request, attendee_pk):
        attendee = get_object_or_404(Attend, pk=attendee_pk)
        
        pks = request_attendee_pks_signal.send(self, attendee=attendee)
        
        menu = nav.attendee_menu.render(event_pk=request.bound_object.pk,
                                        attendee_pk=attendee_pk,
                                        user_pk=attendee.user.pk)
        
        return render_to_response('sadmin/events/attendee/show_pks.html',
                                  {'menu': menu,
                                   'attendee': attendee,
                                   'pks': pks},
                                  context_instance=SAdminContext(request))