from django.core.urlresolvers import reverse

from navtree.navigation import Page

"""
Each SAdmin instance consists of a number of pages related to each other
in a directed acylic graph with a single root page as origin. Multiple
SAdmin instances can be bound together by connecting their graphs.

The route between a given page and the origin of a graph represents
the page's current navigation path. This path can be translated
into an URL such as:

/page1/object1/page2.1/object2/page2.2/

In this case, page1 and object1 belong to one SAdmin instance, and
page2.1, object2 and page.2.2 belong to another SAdmin instance.

In order to render this path, references to objects referenced by
a given page and its predecessors in the navigation path must be
known. This is solved by constructing a navigation stack, containing
references to all objects used in the path.

Each page knows their depth and offset. The sum of these denote how
many objects from the stack belongs to the page. The depth is
controlled by the order of SAdmin instances bound to each other
(each SAdmin instance constains a single object page) and the offset
denotes if the page is placed before of after the object page.

"""

class DirectPage(Page):
 
    def get_url(self, context):
        return self._url   

class SPage(Page):
    offset = 0

    def __init__(self, title, url, parent=None, permission=None, depth=None):
        super(SPage, self).__init__(title, url, parent=parent, permission=permission)

        self.depth = depth or 0

    def get_navigation_stack(self, context):
        navigation_stack = context.get('navigation_stack', [])

        current_object = context.get('original', None) or \
                         context.get('object', None)

        if current_object is not None:
            navigation_stack.append(current_object)

        return navigation_stack

    def to_pk(self, navigation_stack):
        return [obj.pk for obj in navigation_stack]

    def get_url(self, context):
        navigation_stack = self.to_pk(self.get_navigation_stack(context))

        return reverse(self._url,
                       args=navigation_stack[:self.depth+self.offset])

class LeafSPage(SPage):
    offset = 1

class ObjectSPage(SPage):
    offset = 1

    def __init__(self, url, parent=None, permission=None, depth=None):
        super(ObjectSPage, self).__init__('', url, parent=parent, permission=permission, depth=depth)

    def get_title(self, context):
        navigation_stack = self.get_navigation_stack(context)

        current_object = navigation_stack[self.depth]

        return unicode(current_object)

class RemoteSPage(SPage):
    def __init__(self, *args, **kwargs):
        self.url_callback = kwargs.pop('url_callback', None)

        super(RemoteSPage, self).__init__(*args, **kwargs)

    def get_url(self, context):
        if callable(self._url):
            return self._url(context, self.get_navigation_stack(context))
        else:
            return super(RemoteSPage, self).get_url(context)
