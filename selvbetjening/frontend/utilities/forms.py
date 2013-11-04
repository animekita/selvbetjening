import re

from django.core import validators
from django import forms
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.forms.extras.widgets import SelectDateWidget

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Row, Fieldset, Div, HTML

from selvbetjening.core.user.models import SUser

__ALL__ = ('S2FormHelper', 'S2Layout', 'S2Field', 'S2Fieldset', 'S2HorizontalRow', 'S2Submit',
           'S2SubmitCreate', 'S2SubmitUpdate', 'SplitDateWidget')


class S2FormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        horizontal = kwargs.pop('horizontal', False)

        super(S2FormHelper, self).__init__(*args, **kwargs)

        if horizontal:
            self.form_class = 'form-horizontal'
            self.label_class = 'col-lg-2'
            self.field_class = 'col-lg-8'

        self.html5_required = True


class S2Layout(Layout):

    template = "sadmin2/generic/parts/form_layout.html"

    def render(self, *args, **kwargs):

        form = args[0]
        fields = super(S2Layout, self).render(*args, **kwargs)

        return render_to_string(self.template, {'layout': self,
                                                'fields': fields,
                                                'form': form})


class S2Field(Field):
    def __init__(self, *args, **kwargs):

        if 'width' in kwargs:
            kwargs['wrapper_class'] = kwargs.get('wrapper_class', '') + ' col-lg-%s' % kwargs.get('width')

        super(S2Field, self).__init__(*args, **kwargs)


class S2Fieldset(Fieldset):

    def __init__(self, name, *args, **kwargs):
        collapse = kwargs.pop('collapse', True)
        show_help_text = kwargs.pop('show_help_text', True)
        help_text = kwargs.pop('help_text', None)

        if not show_help_text:
            kwargs['css_class'] = ' '.join([kwargs.get('css_class', ''), 'hide-help-block'])

        self.template = "sadmin2/generic/parts/form_fieldset_collapse.html" if collapse else "sadmin2/generic/parts/form_fieldset.html"

        args = [(S2Field(arg) if isinstance(arg, str) else arg) for arg in args]
        super(S2Fieldset, self).__init__(name, *args, **kwargs)

        if help_text is not None:
            self.fields = [HTML('<p>%s</p>' % unicode(help_text))] + list(self.fields)


class S2HorizontalRow(Row):
    def __init__(self, *args, **kwargs):
        """
        Formatting of inlined elements in horizontal rows is not pretty. Lets apply some col-lg-* hacking.

        - Add a col-lg-2 to offset left-hand-side labels
        - Add a col-lg-9 representing the useful span (avoiding the right-hand-side padding)

        We add given fields to this second div.

        """

        super(S2HorizontalRow, self).__init__(Div(css_class='col-lg-2'), Div(*args, css_class='col-lg-9'), **kwargs)


class S2Submit(Submit):
    pass


class S2SubmitCreate(S2Submit):

    def __init__(self, name=None):
        super(S2SubmitCreate, self).__init__('create' if name is None else name, _('Create'))


class S2SubmitUpdate(S2Submit):

    def __init__(self, name=None):
        super(S2SubmitUpdate, self).__init__('update' if name is None else name, _('Update'))


class S2JavaScriptButton(S2Submit):
    input_type = 'button'

    def __init__(self, label, href):
        super(S2JavaScriptButton, self).__init__('action', label, onclick=href)


from django.forms.widgets import TextInput


class SplitDateWidget(SelectDateWidget):

    def create_select(self, name, field, value, val, choices):
        if 'id' in self.attrs:
            id_ = self.attrs['id']
        else:
            id_ = 'id_%s' % name

        #if not (self.required and val):

        local_attrs = self.build_attrs(id=field % id_)
        local_attrs['width'] = 2

        s = TextInput()
        select_html = s.render(field % name, val, local_attrs)

        if 'day' in field:
            label = 'dd'
        elif 'month' in field:
            label = 'mm'
        else:
            label = 'yyyy'

        html = \
            """
            <div class="input-group col-lg-4">
                <span class="input-group-addon">%s</span>
                %s
            </div>
            """ % (label, select_html)

        return html

