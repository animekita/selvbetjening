from django.utils.safestring import mark_safe
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.core.urlresolvers import reverse

search_map = {}

def register_object_search_page(app_label, object_name, url):
    search_map['%s-%s' % (app_label, object_name)] = url

class SAdminForeignKeyRawIdWidget(ForeignKeyRawIdWidget):
    """
    Modified version of the Django ForeignKeyRawIdWidget accepting an alternate url.
    """
    def __init__(self, rel, attrs=None, using=None):
        self.url = reverse(search_map['%s-%s' % (rel.to._meta.app_label, rel.to._meta.object_name.lower())])

        super(SAdminForeignKeyRawIdWidget, self).__init__(rel, attrs=attrs, using=using)

    def render(self, name, value, attrs=None):
        related_url = '../../../%s/%s/' % (self.rel.to._meta.app_label, self.rel.to._meta.object_name.lower())

        output = super(SAdminForeignKeyRawIdWidget, self).render(name, value, attrs=attrs)
        output = output.replace(related_url, self.url)

        return mark_safe(output)