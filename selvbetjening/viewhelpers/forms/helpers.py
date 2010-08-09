from uni_form.helpers import Fieldset, HTML

class InlineFieldset(Fieldset):
    def __init__(self, *args, **kwargs):
        ext_class = kwargs.pop('ext_class', None)
        help_text = kwargs.pop('help_text', None)
        large_hints = kwargs.pop('large_hints', False)

        super(InlineFieldset, self).__init__(*args, **kwargs)

        self.css = 'inlineLabels'

        if large_hints:
            self.css = self.css + ' optionList'

        if ext_class is not None:
            self.css = self.css + ' ' + ext_class

        if help_text is not None:
            self.fields = [HTML(unicode(help_text))] + list(self.fields)