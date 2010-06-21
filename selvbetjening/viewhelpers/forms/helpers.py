from uni_form.helpers import Fieldset

class InlineFieldset(Fieldset):
    def __init__(self, *args, **kwargs):
        super(InlineFieldset, self).__init__(*args, **kwargs)
        self.css = 'inlineLabels'