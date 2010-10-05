from django.core.urlresolvers import reverse

class Navigation(object):
    def __init__(self):
        self.options = []

    def register(self, option):
        self.options.append(option)

    def __iter__(self):
        return self.options.__iter__()

class Option(object):
    def __init__(self, label, url):
        self.label = label
        self.url = url

class OptionProxy(object):
    """
    Wraps an option while containing data and methods which is request specific.
    """

    def __init__(self, option, context):
        self.option = option
        self.context = context

    @property
    def url(self):
        if callable(self.option.url):
            return self.option.url(self.context)
        else:
            return reverse(self.option.url)

    @property
    def label(self):
        return self.option.label

registry = {}

registry['main'] = Navigation() # default sadmin navigation
