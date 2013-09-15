from django.contrib.contenttypes.generic import GenericStackedInline


class TranslationInline(GenericStackedInline):
    extra = 0