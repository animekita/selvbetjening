def form_collection_builder(form_classes):
    """
    Takes a list of form classes, returning a FormCollection
    with combined is_valid and save methods.
    """

    class FormCollection(object):
        def __init__(self, *args, **kwargs):
            self._forms = [klass(*args, **kwargs) for klass in self._form_classes]

        def __iter__(self):
            return iter(self._forms)

        def is_valid(self):
            error = False

            for form in self._forms:
                error = form.is_valid() or error

            return error

        def save(self, *args, **kwargs):
            for form in self._forms:
                form.save(*args, **kwargs)

    FormCollection._form_classes = form_classes

    return FormCollection