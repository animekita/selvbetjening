# -- encoding: utf-8 --

from django.utils.translation import ugettext as _
from django.db.models import Count
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.admin.util import unquote

from selvbetjening.core.translation.admin import TranslationInline
from selvbetjening.core.events.models import Event
from selvbetjening.core.events.models import Event, AttendState, Attend, AttendState
from selvbetjening.core.events.processor_handlers import change_selection_processors, checkin_processors
from selvbetjening.core.events.forms import PaymentForm, OptionForms
from selvbetjening.core.invoice.models import Invoice, Payment
from selvbetjening.core import ObjectWrapper

from selvbetjening.sadmin.base.sadmin import site, SModelAdmin, SBoundModelAdmin
from selvbetjening.sadmin.base.views import generic_search_page_unsecure
from selvbetjening.sadmin.base.sadmin import SAdminContext
from selvbetjening.sadmin.base.decorators import sadmin_access_required

from forms import CheckinForm, AttendeeForm
import views
import nav

class AttendeeAdmin(SBoundModelAdmin):
    class Meta:
        app_name = 'events'
        name = 'attendee'
        model = Attend
        bound_model = Event

    changelist_menu = 'event'

    def in_balance(attend):
        return attend.invoice.in_balance()
    in_balance.boolean = True

    list_filter = ('state',)
    list_per_page = 50
    list_display = ('user', 'user_first_name', 'user_last_name', 'state', in_balance)

    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    raw_id_fields = ('user', 'event', 'invoice')

    #def get_urls(self):
        #from django.conf.urls.defaults import patterns, url

        #info = self.model._meta.app_label, self.model._meta.module_name

        #urlpatterns = patterns('',
                               #url(r'^(.+)/selections/change/',
                                   #self.admin_site.admin_view(admin_views.change_selections),
                                   #name='%s_%s_selections_change' % info),
                               #url(r'^(.+)/billing/',
                                   #self.admin_site.admin_view(admin_views.billing),
                                   #name='%s_%s_billing' % info),
                               #url(r'^(.+)/checkin/',
                                   #self.admin_site.admin_view(admin_views.checkin),
                                   #name='%s_%s_checkin' % info),
                               #url(r'^(.+)/checkout/',
                                   #self.admin_site.admin_view(admin_views.checkout),
                                   #name='%s_%s_checkout' % info),
                               #)

        #urlpatterns += super(AttendAdmin, self).get_urls()

        #return urlpatterns

    def changelist_view(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}

        extra_context['menu'] = nav.event_menu.render({'original': request.bound_object})

        return super(AttendeeAdmin, self).changelist_view(request, extra_context)

    def change_view(self, request, object_id, extra_context=None):
        extra_context = extra_context or {}
        extra_context['menu'] = nav.attendee_menu.render({
            'event': request.bound_object,
            'attendee': unquote(object_id)})

        return super(AttendeeAdmin, self).change_view(request, object_id, extra_context)

    def queryset(self, request):
        qs = super(SBoundModelAdmin, self).queryset(request)

        return qs.filter(event=request.bound_object)

class EventAdmin(SModelAdmin):
    class Meta:
        app_name = 'events'
        name = 'event'
        model = Event

    add_form_template = 'sadmin/events/event/create.html'
    change_form_template = 'sadmin/events/event/change.html'

    def attendees_count(event):
        return event.attendees.count()
    attendees_count.short_description = 'Attendees'
    attendees_count.admin_order_field = 'attend__count'

    list_display = ('title', attendees_count, 'startdate',)
    list_filter = ('registration_open',)

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
        info = self.model._meta.app_label, self.model._meta.module_name

        urlpatterns = super(EventAdmin, self).get_urls()

        urlpatterns = patterns('',
            url(r'^(?P<event_pk>[0-9]+)/statistics/$',
                self._wrap_view(views.view_statistics),
                name='%s_%s_statistic' % info),
            (r'^(?P<bind_pk>[0-9]+)/attendees/', include(AttendeeAdmin().urls)),
        ) + urlpatterns

        return urlpatterns

site.register('events', EventAdmin)