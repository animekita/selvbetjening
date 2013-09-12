
from django import template

from selvbetjening.sadmin2.menu import breadcrumbs

register = template.Library()


class breadcrumb_iterator(object):

    def __init__(self, id):
        self.current = breadcrumbs.get(id, None)

    def __iter__(self):
        return self

    # Python 3 compatibility
    def __next__(self):
        return self.next()

    def next(self):
        if self.current is not None:
            ret = self.current
            self.current = breadcrumbs[self.current['parent']] if 'parent' in self.current else None

            return ret
        else:
            raise StopIteration()

@register.inclusion_tag('sadmin2/parts/breadcrumbs.html', takes_context=True)
def sadmin2_breadcrumbs(context, id):

    return {
        'sadmin2_breadcrumbs': reversed(list(breadcrumb_iterator(id))),
    }