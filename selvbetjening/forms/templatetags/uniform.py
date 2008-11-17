from django import template
from django import forms
from django.utils import safestring
from django.conf import settings

from selvbetjening.forms.uniform import *

register = template.Library()

class IncompatibleFormError:
    pass

@register.filter(name='uniform_add')
def uniform_form_rendering(form, submitText=None):
    render = ''

    if form.non_field_errors():
        render += '<div id="errorMsg">\n'
        render += form.non_field_errors().as_ul()
        render += '</div>\n'

    if hasattr(form, 'Meta') and hasattr(form.Meta, 'layout'):
        for section in form.Meta.layout:
            render += '<fieldset class="inlineLabels"><legend>' + section[0] + '</legend>\n'

            if len(section) == 3 and len(section[2]) > 0:
                render += '<div class="ctrlHolder blockLabels">'
                render += '<p>%s</p>' % section[2]
                render += '</div>'


            for item_name in section[1]:
                if isinstance(item_name, tuple):
                    render += render_input(form[item_name[0]], args=item_name[1])
                else:
                    render += render_input(form[item_name])
            render += '</fieldset>\n'

    else:
        items = ''

        for item in form:
            items += render_input(item)

        if items != '':
            render += '<fieldset class="inlineLabels">' + items + '</fieldset>\n'

    if submitText is not None:
        render += render_Submit(submitText)

    return safestring.mark_safe(render)

@register.filter(name='uniform_start')
def uniform_startrendering(form):
    if form.is_multipart:
        return safestring.mark_safe('<form enctype="multipart/form-data" method="post" action="" class="uniForm">\n\n')
    else:
        return safestring.mark_safe('<form method="post" action="" class="uniForm">\n\n')

@register.filter(name='uniform_end')
def uniform_endrendering(form):
    return safestring.mark_safe('</form>')

@register.filter(name='uniform')
def uniform_formrendering(form, submitText=None):
    if not isinstance(form, forms.Form) and not isinstance(form, forms.ModelForm):
        raise IncompatibleFormError()

    render = uniform_startrendering(form)
    render += uniform_form_rendering(form, submitText)
    render += uniform_endrendering(form)

    return safestring.mark_safe(render)

@register.tag
def uniform_header(parser, token):
        return UniformHeaderNode()

class UniformHeaderNode(template.Node):

        def render(self, context):
                return safestring.mark_safe('<link rel="stylesheet" type="text/css" href="%scss/compressed/uni-form.css" media="screen, projection" />\n<script type="text/javascript" src="%sjs/datepicker.js"></script>\n<link href="%scss/compressed/datepicker.css" rel="stylesheet" type="text/css" />' %
                                            (settings.MEDIA_URL, settings.MEDIA_URL, settings.MEDIA_URL))

def render_input(item, args={ }):
    if isinstance(item.field.widget, (forms.TextInput,)) and hasattr(item.field, 'choices'):
        return UniformInputSelectbox(item, args=args).render()
    elif isinstance(item.field.widget, (forms.TextInput, forms.PasswordInput)):
        return UniformInputText(item, args=args).render()
    elif isinstance(item.field.widget, (forms.CheckboxInput)):
        return UniformInputCheckbox(item, args=args).render()
    elif isinstance(item.field.widget, (forms.Textarea)):
        return UniformInputTextarea(item, args=args).render()
    elif isinstance(item.field.widget, (forms.FileInput)):
        return UniformInputFile(item, args=args).render()
    else:
        return '<div style="color: red">ERROR: UNKNOWN INPUT TYPE %s</div>\n' % item.name

def render_Submit(text):
    return '<fieldset class="inlineLabels"><div class="buttonHolder"><button type="submit" class="submitButton">%s</button></div></fieldset>' % text