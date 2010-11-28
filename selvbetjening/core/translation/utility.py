from django.contrib.contenttypes.models import ContentType
from django.utils.translation import get_language
from django.conf import settings

from models import Translation

def translate_model(object, locale=None):
    if locale is None:
        locale = get_language()

    if locale == settings.LANGUAGE_CODE:
        # do not translate "default" langauge
        return object

    fields = object.Translation.fields

    for field in fields:
        try:
            content_type = ContentType.objects.get_for_model(object.__class__)

            translation = Translation.objects.get(content_type=content_type,
                                                  object_id=object.pk,
                                                  locale=locale, field=field)
            setattr(object, field, translation.translation)
        except Translation.DoesNotExist:
            pass # do not translate, keep original translation

    return object
