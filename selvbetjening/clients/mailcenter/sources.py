from django.core import signals
from django.utils.translation import ugettext as _
from django.db.models.signals import post_save
from django.contrib.auth.models import User

default_parameters = [User]

source_triggered = signals.Signal(providing_args=['source_key', 'user'])

class SourceRegistry(object):
    def __init__(self):
        self.sources = {}

    def register(self, key, name, extra_parameters, signal):
        source = {'name': name,
                  'parameters': default_parameters + extra_parameters}

        self.sources[key] = source

        def handler(sender, **kwargs):
            user = kwargs.pop('user')
            source_triggered.send(self, source_key=key, user=user)

        signal.connect(handler)

    def get_choices(self):
        return [(key, self.sources[key]['name']) for key in self.sources]

    def get(self, key):
        return self.sources[key]

registry = SourceRegistry()