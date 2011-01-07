from django.utils.safestring import mark_safe
from django.contrib.admin.widgets import ForeignKeyRawIdWidget

class SAdminForeignKeyRawIdWidget(ForeignKeyRawIdWidget):
    """
    Modified version of the Django ForeignKeyRawIdWidget accepting an alternate url.
    """
    def __init__(self, rel, attrs=None, using=None, url=None):
        self.url = url
        super(SAdminForeignKeyRawIdWidget, self).__init__(rel, attrs=attrs, using=using)

    def render(self, name, value, attrs=None):
        related_url = '../../../%s/%s/' % (self.rel.to._meta.app_label, self.rel.to._meta.object_name.lower())

        output = super(SAdminForeignKeyRawIdWidget, self).render(name, value, attrs=attrs)
        if self.url is not None:
            output = output.replace(related_url, self.url)

        return mark_safe(output)