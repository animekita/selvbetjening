from selvbetjening.sadmin.base.sadmin import site

from admins.user import UserAdmin

site.register('members', UserAdmin)