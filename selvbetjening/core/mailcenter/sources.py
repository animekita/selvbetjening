from django.core import signals
from django.utils.translation import ugettext as _
from django.db.models.signals import post_save
from django.contrib.auth.models import User

default_parameters = [User]

source_triggered = signals.Signal(providing_args=['source_key', 'user', 'kwargs'])

class SourceRegistry(object):
    def __init__(self):
        self.sources = {}

    def register(self, source):
        self.sources[source.key] = source

    def __iter__(self):
        return iter([(key, self.sources[key].name) for key in self.sources])
    
    def get(self, key):
        return self.sources[key]

registry = SourceRegistry()

class Source(object):
    def __init__(self, key, name, extra_parameters):
        self.key = key
        self.name = name
        self.parameters = default_parameters + extra_parameters
        
        registry.register(self)
    
    def trigger(self, user, **kwargs):
        source_triggered.send(self, source_key=self.key, user=user, kwargs=kwargs)
    