from uni_form import helpers

class Fieldset(helpers.Fieldset):
    def __init__(self, *args, **kwargs):
        ext_class = kwargs.pop('ext_class', None)
        help_text = kwargs.pop('help_text', None)
        large_hints = kwargs.pop('large_hints', False)

        super(Fieldset, self).__init__(*args, **kwargs)

        if large_hints:
            self.css = self.css + ' optionList' if self.css else 'optionList'

        if ext_class is not None:
            self.css = self.css + ' ' + ext_class if self.css else ext_class

        if help_text is not None:
            self.fields = [helpers.HTML(unicode(help_text))] + list(self.fields)

class InlineFieldset(Fieldset):
    def __init__(self, *args, **kwargs):
        ext_class = kwargs.get('ext_class', None)
        
        if ext_class is None:
            ext_class = 'inlineLabels'
        else:
            ext_class += ' inlineLabels'
            
        kwargs['ext_class'] = ext_class
        
        super(InlineFieldset, self).__init__(*args, **kwargs)