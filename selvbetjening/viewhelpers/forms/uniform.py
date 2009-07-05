from django import forms
from django.utils.encoding import force_unicode

class UniformInputBase(object):

    def __init__(self, input, args=None):
        self.attrs = {}
        self.input = input

        if args is None:
            self.args = {}
        else:
            self.args = args

        if self.args.get('disabled', False):
            self.attrs['DISABLED'] = True

    def error_list(self):
        if self.input.errors:
            return '<p class="errorField"><strong>' + self.input.errors.as_text() + '</strong></p>\n'
        else:
            return ''

    def label(self):
        if self.input.field.required:
            return self.input.label_tag('<em>*</em> ' + force_unicode(self.input.label)) + '\n'
        else:
            return self.input.label_tag() + '\n'

    def help_text(self):
        if self.input.help_text is not None:
            return '<p class="formHint">' + self.input.help_text + '</p>\n'

    def render_container(self, content):
        cls = ''
        if self.input.errors:
            cls = ' error'
        if self.args.get('display', '') == 'block':
            cls += ' blockLabels'

        return '<div class="ctrlHolder%s">\n' % cls + content + '</div>\n\n'

    def render_input_hidden(self):
        return self.input.as_widget(widget=forms.widgets.HiddenInput())

    def render_input(self):
        return self.input.as_widget(attrs=self.attrs)

    def render(self):
        if self.args.get('display', '') == 'hidden':
            return self.render_input_hidden()
        else:
            return self.render_container(self.error_list() + self.label() + self.render_input() + self.help_text())

class UniformInputText(UniformInputBase):

    def render(self):
        self.attrs = {'class' : 'text'}

        if self.args.get('title', False):
            self.attrs['class'] += ' title'

        if self.args.get('display', '') == 'block':
            self.attrs['class'] += ' textInputWide'
        else:
            self.attrs['class'] += ' textInput'

        if isinstance(self.input.field, forms.DateField):
            self.attrs['class'] += ' w8em format-d-m-y divider-dash highlight-days-67'

        return UniformInputBase.render(self)

class UniformInputTextarea(UniformInputBase):

    def render(self):
        self.attrs = {'class' : 'text'}

        if self.args.get('display', '') == 'block':
            self.attrs['class'] += ' textInputWide'

        return UniformInputBase.render(self)

class UniformInputCheckbox(UniformInputBase):

    def render_input(self):
        required = ''
        if self.input.field.required:
            required = ' <em>*</em> '

        help = ''
        if self.input.help_text is not None and len(self.input.help_text) > 0:
            help = ': <i>' + self.input.help_text + '</i>'

        return self.input.label_tag(self.input.as_widget(attrs=self.attrs) + required + self.input.label + help) + '\n'

    def render(self):
        return self.render_container(self.error_list() + '<div>' + self.render_input() + '</div>')

class UniformInputSelectbox(UniformInputBase):

    def render_input(self):
        self.attrs = {'class' : 'selectInput'}

        return self.input.as_widget(widget=forms.widgets.Select(choices=self.input.field.choices), attrs=self.attrs)

class UniformInputFile(UniformInputText):

    def __init__(self, *args, **kwargs):
        super(UniformInputFile, self).__init__(*args, **kwargs)

        self.attrs = {'class' : 'fileUpload text'}