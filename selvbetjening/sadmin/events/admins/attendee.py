# -- encoding: utf-8 --

from django.utils.translation import ugettext as _
from django.contrib.admin.util import unquote
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib import messages

from selvbetjening.core.events.models import Event, Attend, request_attendee_pks_signal
from selvbetjening.core.events.processor_handlers import change_selection_processors
from selvbetjening.core.events.forms import OptionForms
from selvbetjening.core.forms import form_collection_builder

from selvbetjening.sadmin.base.sadmin import SBoundModelAdmin, SAdminContext

from selvbetjening.sadmin.events import nav
from selvbetjening.sadmin.events.admins.nonattendee import NonAttendeeAdmin
from selvbetjening.sadmin.events.admins.invoice import InvoiceAdmin
from selvbetjening.sadmin.events.forms import PaymentForm, AttendeeForm

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
        
        if request.method == 'POST':
            payment_form = PaymentForm(request.POST)
            attendee_form = AttendeeForm(request.POST, instace=attendee)
            
            forms = form_collection_builder((payment_form, attendee_form))
            
            if forms.is_valid():
                instance = payment_form.save(commit=False)
                instance.invoice = request.bound_object.invoice
                instance.signee = request.user
                
                attendee_form.save()
                
                payment_form = PaymentForm()
                
        else:
            payment_form = PaymentForm()
            attendee_form = AttendeeForm(instance=attendee)
        
        menu = nav.attendee_menu.render(
            event_pk=request.bound_object.pk,
            attendee_pk=attendee_pk)
        
        return render_to_response('sadmin/events/event/attendee.html',
                                  {'menu': menu,
                                   'attendee': attendee,
                                   'payment_form': payment_form,
                                   'attendee_form': attendee_form},
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
                                        attendee_pk=attendee_id)

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
                                        attendee_pk=attendee_pk)
        
        return render_to_response('sadmin/events/attendee/show_pks.html',
                                  {'menu': menu,
                                   'attendee': attendee,
                                   'pks': pks},
                                  context_instance=SAdminContext(request))