from django.contrib.contenttypes.generic import GenericTabularInline

from selvbetjening.core.translation.models import Translation

class TranslationInline(GenericTabularInline):
    model = Translation