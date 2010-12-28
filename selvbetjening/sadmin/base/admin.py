from django.contrib.contenttypes.generic import GenericStackedInline

from selvbetjening.core.translation.models import Translation

class TranslationInline(GenericStackedInline):
    model = Translation
    extra = 0