from django.contrib.contenttypes.models import ContentType
from django.utils.translation import get_language
from django.conf import settings
from copy import deepcopy

from models import Translation

def translate_model(obj, locale=None, copy=False):
    if copy:
        obj = deepcopy(obj)

    if locale is None:
        locale = get_language()

    if locale == settings.LANGUAGE_CODE:
        # do not translate "default" langauge
        return obj

    fields = obj.Translation.fields

    content_type = ContentType.objects.get_for_model(obj.__class__)

    for field in fields:
        try:
            translation = Translation.objects.get(content_type=content_type,
                                                  object_id=obj.pk,
                                                  locale=locale, field=field)
            setattr(obj, field, translation.translation)
        except Translation.DoesNotExist:
            pass # do not translate, keep original translation

    return obj
