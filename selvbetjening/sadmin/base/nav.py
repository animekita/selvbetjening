from django.core.urlresolvers import reverse

class OptionProxy(object):
    """
    Wraps an option while containing data and methods which is request specific.
    """

    def __init__(self, option, context):
        self.option = option
        self.context = context

    @property
    def available(self):
        return self.option.available(self.context['user'])

    @property
    def url(self):
        if callable(self.option.url):
            return self.option.url(self.context)
        else:
            return reverse(self.option.url)

    @property
    def label(self):
        return self.option.label

    def __iter__(self):
        elements = [OptionProxy(element, self.context) for element in self.option]
        return elements.__iter__()

class Navigation(object):
    def __init__(self, label=None):
        self.label = label
        self.options = []

    def register(self, option):
        self.options.append(option)

    def render(self, context):
        return [OptionProxy(option, context) for option in self]

    def __iter__(self):
        return self.options.__iter__()

class Option(object):
    def __init__(self, label, url, available=None):
        self.label = label
        self.url = url
        self.available = available if not None else lambda user: True

registry = {}

registry['main'] = Navigation() # default sadmin navigation
