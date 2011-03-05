from django.core.urlresolvers import reverse

from navtree.navigation import Page

class SPage(Page):
    def __init__(self, title, url, parent=None, context_args=None, permission=None):
        super(SPage, self).__init__(title, url, parent=parent, name=url, permission=permission)

        self.context_args = context_args
        
    def _get_current_object(self, context):
        current_object = context.get('bound_object', None)
        
        if current_object is None:
            current_object = context.get('original', None)

        if current_object is None:
            current_object = context['object']
        
        return current_object

class LeafSPage(SPage):
    def get_url(self, context):
        current_object = self._get_current_object(context)

        return reverse(self._url, args=[current_object.pk])

class ObjectSPage(SPage):
    def __init__(self, url, parent=None, permission=None):
        super(ObjectSPage, self).__init__('', url, parent=parent, permission=permission)

    def get_title(self, context):
        current_object = self._get_current_object(context)
        
        return unicode(current_object)

    def get_url(self, context):
        current_object = self._get_current_object(context)

        return reverse(self._url, args=[current_object.pk])

class BoundSPage(SPage):
    def get_url(self, context):
        bound_object = context.get('bound_object', None)
        
        if bound_object is None:
            bound_object = self._get_current_object(context)
        
        return reverse(self._url, kwargs={'bind_pk': bound_object.pk})
    
    def _get_current_object(self, context):
        current_object = context.get('original', None)
            
        if current_object is None:
            current_object = context['object']
            
        return current_object
    
class BoundLeafSPage(BoundSPage):
    def get_url(self, context):
        bound_object = context.get('bound_object')
        current_object = self._get_current_object(context)

        return reverse(self._url, args=[bound_object.pk, current_object.pk])
    
class BoundObjectSPage(BoundSPage):
    def __init__(self, url, parent=None, permission=None):
        super(BoundObjectSPage, self).__init__('', url, 
                                               parent=parent, 
                                               permission=permission)
    
    def get_title(self, context):
        current_object = self._get_current_object(context)
        
        return unicode(current_object)

    def get_url(self, context):
        bound_object = context.get('bound_object')
        current_object = self._get_current_object(context)

        return reverse(self._url, args=[bound_object.pk, current_object.pk])
