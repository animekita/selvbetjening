from django.contrib.contenttypes.generic import GenericTabularInline

from models import Translation

class TranslationInline(GenericTabularInline):
    model = Translation