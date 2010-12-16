from selvbetjening.sadmin.base.sadmin import site

from admins.emailspecification import EmailSpecificationAdmin
import nav

site.register('mailcenter', EmailSpecificationAdmin)