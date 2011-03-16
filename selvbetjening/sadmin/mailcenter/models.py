from selvbetjening.sadmin.base.sadmin import site

from admins.emailspecification import EmailSpecificationAdmin

site.register('mailcenter', EmailSpecificationAdmin)