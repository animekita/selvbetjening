from crispy_forms import layout


class SFieldset(layout.Fieldset):
    def __init__(self, *args, **kwargs):
        ext_class = kwargs.pop('ext_class', None)
        help_text = kwargs.pop('help_text', None)
        large_hints = kwargs.pop('large_hints', False)

        super(SFieldset, self).__init__(*args, **kwargs)

        if large_hints:
            self.css_class = self.css_class + ' optionList' if self.css_class else 'optionList'

        if ext_class is not None:
            self.css_class = self.css_class + ' ' + ext_class if self.css_class else ext_class

        if help_text is not None:
            self.fields = [layout.HTML('<p>%s</p>' % unicode(help_text))] + list(self.fields)
