from django.contrib.contenttypes.generic import GenericStackedInline

from models import Translation

class TranslationInline(GenericStackedInline):
    model = Translation
    extra = 0