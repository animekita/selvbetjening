from selvbetjening.sadmin.base.sadmin import site

from admins.event import EventAdmin
import nav

site.register('events', EventAdmin)