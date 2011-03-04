from selvbetjening.sadmin.base.sadmin import site

from admins.user import UserAdmin
from admins.group import GroupAdmin
import nav

site.register('members', UserAdmin)