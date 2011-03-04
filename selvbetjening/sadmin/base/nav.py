from django.core.urlresolvers import reverse

from navtree.navigation import Page

class SPage(Page):
    def __init__(self, title, url, parent=None, context_args=None, permission=None):
        super(SPage, self).__init__(title, url, parent=parent, name=url, permission=permission)

        self.context_args = context_args

class BoundSPage(SPage):
    def get_url(self, context):
        bound_object = context.get('bound_object')

        return reverse(self._url, args=[bound_object.pk])

class LeafSPage(SPage):
    def get_url(self, context):
        original = context.get('original')

        return reverse(self._url, args=[original.pk])

class BoundLeafSPage(SPage):
    def get_url(self, context):
        bound_object = context.get('bound_object')
        original = context.get('original')

        return reverse(self._url, args=[bound_object.pk, original.pk])

class ObjectSPage(SPage):
    def __init__(self, url, parent=None, permission=None):
        super(ObjectSPage, self).__init__('', url, parent=parent, permission=permission)

    def get_title(self, context):
        bound_object = context.get('bound_object', None)
        original = context.get('original', None)

        if bound_object:
            return unicode(bound_object)
        else:
            return unicode(original)

    def get_url(self, context):
        bound_object = context.get('bound_object', None)
        original = context.get('original', None)

        if bound_object:
            return reverse(self._url, args=[bound_object.pk])
        else:
            return reverse(self._url, args=[original.pk])

class BoundObjectSPage(ObjectSPage):
    def get_title(self, context):
        original = context.get('original')

        return unicode(original)

    def get_url(self, context):
        bound_object = context.get('bound_object')
        original = context.get('original')

        return reverse(self._url, args=[bound_object.pk, original.pk])
