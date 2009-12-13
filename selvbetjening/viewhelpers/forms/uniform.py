from django import forms
from django.utils.encoding import force_unicode

class UniformException(Exception):
    pass

class UniformInputBase(object):

    def __init__(self, input, args=None, is_child=False):
        self.attrs = {}
        self.input = input
        self.is_child = is_child

        if is_child:
            self.attrs['class'] = 'child_input'

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
        if self.is_child:
            return content

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

    def render_children(self, children=None):
        if children is None:
            children = []

        rendered_children = ''
        for child in children:
            rendered_children += child.render()

        return rendered_children

    def render(self, children=None):
        if self.args.get('display', '') == 'hidden':
            return self.render_input_hidden()
        else:
            return self.render_container(self.error_list() + self.label() + self.render_input() + self.help_text() + self.render_children(children))

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

    def render(self, *args, **kwargs):
        self.attrs = {'class' : 'text'}

        if self.args.get('display', '') == 'block':
            self.attrs['class'] += ' textInputWide'

        return super(UniformInputTextarea, self).render(*args, **kwargs)

class UniformInputCheckbox(UniformInputBase):

    def render_input(self):
        required = ''
        if self.input.field.required:
            required = ' <em>*</em> '

        help = ''
        if self.input.help_text is not None and len(self.input.help_text) > 0:
            help = self.input.help_text

        if not self.is_child:
            parent_input = '$("#id_%s")' % self.input.name

            js  = '<script type="text/javascript">'

            js += '$(document).ready(function(){'
            js += ' update_child_inputs(%s);' % parent_input
            js += '});'

            js += '%s.change(function() {' % parent_input
            js += ' update_child_inputs(%s);' % parent_input
            js += '});'

            js += '</script>'
        else:
            js = ''

        #$(".revision_line").click(function () {
        #$(this).next().find("table").toggle("normal");
        #});

        return self.input.label_tag(self.input.as_widget(attrs=self.attrs) + required + self.input.label) + help + js + '\n'

    def render(self, children=None):
        return self.render_container(self.error_list() + '<div>' + self.render_input() + '</div>' + self.render_children(children))

class UniformInputSelectbox(UniformInputBase):

    def render_input(self):
        self.attrs['class'] = self.attrs.get('class', '') + ' selectInput'

        return self.input.as_widget(widget=forms.widgets.Select(choices=self.input.field.choices), attrs=self.attrs)

class UniformInputFile(UniformInputText):

    def __init__(self, *args, **kwargs):
        super(UniformInputFile, self).__init__(*args, **kwargs)

        self.attrs = {'class' : 'fileUpload text'}

class UniformInputSelectDate(UniformInputBase):
    pass

class UniformInputRadio(UniformInputBase):
    pass
