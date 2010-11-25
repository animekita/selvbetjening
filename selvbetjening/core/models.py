from django.db import models
from south.modelsinspector import add_introspection_rules
from django.core import exceptions

add_introspection_rules([], ["^selvbetjening\.core\.models\.ListField"])

class ListField(models.TextField):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self.token = kwargs.pop('token', ',')
        super(ListField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value: return
        if isinstance(value, list):
            return value
        return value.split(self.token)

    def get_db_prep_value(self, value):
        if not value: return
        assert(isinstance(value, list) or isinstance(value, tuple))
        return self.token.join([unicode(s) for s in value])

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)

    def validate(self, values, model_instance):
        if isinstance(values, (list, tuple)):
            for value in values:
                super(ListField, self).validate(value, model_instance)
        else:
            raise exceptions.ValidationError(self.error_messages['invalid_choice'] % value)
