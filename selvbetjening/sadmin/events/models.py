from selvbetjening.sadmin.base.sadmin import site

from admins.event import EventAdmin

site.register('events', EventAdmin)