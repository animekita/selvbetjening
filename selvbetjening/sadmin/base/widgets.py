from django.utils.safestring import mark_safe
from django.contrib.admin.widgets import ForeignKeyRawIdWidget

from selvbetjening.core import ObjectWrapper

class SAdminForeignKeyRawIdWidget(ForeignKeyRawIdWidget):
    """
    Modified version of the Django ForeignKeyRawIdWidget accepting an alternate url.
    """
    def __init__(self, rel, admin_site, attrs=None, using=None):

        admin_site_mock = ObjectWrapper(admin_site)
        admin_site_mock._registry = [rel.to]

        super(SAdminForeignKeyRawIdWidget, self).__init__(rel, admin_site_mock, attrs=attrs, using=using)

    def render(self, name, value, attrs=None):

        return super(SAdminForeignKeyRawIdWidget, self).render(name, value, attrs=attrs)
