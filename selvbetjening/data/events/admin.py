# -- encoding: utf-8 --

from django.utils.translation import ugettext as _
from django.contrib.admin import ModelAdmin, TabularInline
from django.contrib.auth.models import User

from django import shortcuts
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.contrib.admin.views.main import ChangeList
from django.contrib.admin.helpers import AdminForm

from selvbetjening.core.selvadmin.admin import site

from models import Event, Attend, Option, OptionGroup, SubOption, Selection
import admin_views

class EventAdmin(ModelAdmin):
    def changelist_item_actions(self, event):

        actions = u"""
        <a href="%s"><input type="button" value="Statistik"/></a>
        """ % reverse('admin:events_event_stats', args=[event.id,])

        actions += u"""
        <a href="%s?event__id__exact=%s"><input type="button" value="Tilmeldte"/></a>
        """ % (reverse('admin:events_attend_changelist'), event.id)

        actions += u"""
        <a href="%s"><input type="button" value="Tilmeld person"/></a>
        """ % reverse('admin:events_event_attend', args=[event.id,])

        actions += u"""
        <a href="%s"><input type="button" value="Indstillinger"/></a>
        """ % reverse('admin:events_event_change', args=[event.id,])

        return actions

    changelist_item_actions.allow_tags = True
    changelist_item_actions.short_description = _('Actions')

    list_display = ('title', 'startdate', 'changelist_item_actions')

    fieldsets = (
        (None, {
            'fields' : ('title', 'description', 'startdate', 'enddate', 'registration_open'),
        }),
        (_('Conditions'), {
            'fields' : ('maximum_attendees',),
            'classes' : ('collapse', ),
        }),
        (_('Registration Confirmation'), {
            'fields' : ('show_registration_confirmation', 'registration_confirmation'),
            'classes' : ('collapse', ),
        }),
        (_('Change Confirmation'), {
            'fields' : ('show_change_confirmation', 'change_confirmation'),
            'classes' : ('collapse', ),
        }),
        (_('Invoice page'), {
            'fields' : ('show_invoice_page', 'invoice_page'),
            'classes' : ('collapse', ),
        }),
    )

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url

        info = self.model._meta.app_label, self.model._meta.module_name

        urlpatterns = patterns('',
            url(r'^(.+)/stats/',
                self.admin_site.admin_view(admin_views.event_statistics),
                name='%s_%s_stats' % info),
            url(r'^(.+)/attend/',
                self.admin_site.admin_view(admin_views.add_user),
                name='%s_%s_attend' % info),
            )

        urlpatterns += super(EventAdmin, self).get_urls()

        return urlpatterns

site.register(Event, EventAdmin)

class AttendAdmin(ModelAdmin):
    def changelist_item_actions(attend):
        actions = ''

        actions += u"""
        <a href="%s"><input type="button" value="Ændre tilvalg"/></a>
        """ % reverse('admin:events_attend_selections_change', args=[attend.pk])

        actions += u"""
        <a href="%s"><input type="button" value="Billing"/></a>
        """ % reverse('admin:events_attend_billing', args=[attend.pk])

        if not attend.has_attended:
            actions += u"""
            <a href="%s"><input style="font-weight: bold;" type="button" value="Checkin"/></a>
            """ % reverse('admin:events_attend_checkin', args=[attend.pk])
        else:
            actions += u"""
            <a href="%s"><input type="button" value="Checkout"/></a>
            """ % reverse('admin:events_attend_checkout', args=[attend.pk])


        return actions
    changelist_item_actions.allow_tags = True
    changelist_item_actions.short_description = _('Actions')

    def in_balance(attend):
        return attend.invoice.in_balance()
    in_balance.boolean = True

    list_filter = ('event', 'has_attended')
    list_per_page = 50
    list_display = ('user', 'user_first_name', 'user_last_name', 'has_attended',
                    in_balance, changelist_item_actions)

    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    raw_id_fields = ('user', 'event', 'invoice')

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url

        info = self.model._meta.app_label, self.model._meta.module_name

        urlpatterns = patterns('',
                               url(r'^(.+)/selections/change/',
                                   self.admin_site.admin_view(admin_views.change_selections),
                                   name='%s_%s_selections_change' % info),
                               url(r'^(.+)/billing/',
                                   self.admin_site.admin_view(admin_views.billing),
                                   name='%s_%s_billing' % info),
                               url(r'^(.+)/checkin/',
                                   self.admin_site.admin_view(admin_views.checkin),
                                   name='%s_%s_checkin' % info),
                               url(r'^(.+)/checkout/',
                                   self.admin_site.admin_view(admin_views.checkout),
                                   name='%s_%s_checkout' % info),
                               )

        urlpatterns += super(AttendAdmin, self).get_urls()

        return urlpatterns


site.register(Attend, AttendAdmin)

class OptionInline(TabularInline):
    model = Option
    exclude = ['users', ]

class OptionGroupAdmin(ModelAdmin):
    list_display = ('event', 'name',)
    list_filter = ('event',)

    fieldsets = (
        (None, {
            'fields' : ('event', 'name', 'description'),
        }),
        (_('Conditions'), {
            'fields' : ('minimum_selected', 'maximum_selected', 'maximum_attendees', 'freeze_time'),
            'classes' : ('collapse', ),
        }),
        (_('Other'), {
            'fields' : ('order',),
        }),)

    raw_id_fields = ('event',)
    inlines = [OptionInline, ]

site.register(OptionGroup, OptionGroupAdmin)

class SubOptionInline(TabularInline):
    model = SubOption

class SelectionInline(TabularInline):
    model = Selection

    raw_id_fields = ('attendee',)

class OptionAdmin(ModelAdmin):
    list_display = ('group', 'name', 'attendees_count', 'freeze_time')
    list_filter = ('group',)
    fieldsets = (
        (None, {'fields': ('group', 'name', 'description', 'price')}),
        ('Conditions', {'fields': ('freeze_time', 'maximum_attendees', 'order'), 'classes' : ('collapse',)}),
        )

    raw_id_fields = ('group',)
    inlines = [SubOptionInline, SelectionInline]

site.register(Option, OptionAdmin)