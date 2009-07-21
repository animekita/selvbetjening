from django import template
from django import forms
from django.utils import safestring
from django.conf import settings

from selvbetjening.viewhelpers.forms.uniform import *

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

            if len(section) >= 3 and len(section[2]) > 0:
                render += '<div class="ctrlHolder blockLabels">'
                render += '<p>%s</p>' % section[2]
                render += '</div>'

            if len(section) >= 4 and section[3] in form:
                render += '<div class="ctrlHolder blockLabels">'
                render += '<p class="errorField"><strong>' + form[section[3]].errors.as_text() + '</strong></p>\n'
                render += '</div>'

            for item_name in section[1]:
                if isinstance(item_name, tuple):
                    child_inputs = []
                    
                    for child in item_name[1].pop('children', []):
                        child_inputs.append(get_input(form[child], args=item_name[1], is_child=True))
                    
                    render += get_input(form[item_name[0]], args=item_name[1]).render(children=child_inputs)
                    
                else:
                    render += get_input(form[item_name]).render()
            render += '</fieldset>\n'

    else:
        items = ''

        for item in form:
            items += get_input(item).render()

        if items != '':
            render += '<fieldset class="inlineLabels">' + items + '</fieldset>\n'

    if submitText is not None:
        render += render_Submit(submitText)

    return safestring.mark_safe(render)

@register.filter(name='uniform_start')
def uniform_startrendering(form):
    """ DEPRECATED, use uniform_begin """
    if form.is_multipart:
        return safestring.mark_safe('<form enctype="multipart/form-data" method="post" action="" class="uniForm">\n\n')
    else:
        return safestring.mark_safe('<form method="post" action="" class="uniForm">\n\n')

@register.filter(name='uniform_end')
def uniform_endrendering(form):
    """ DEPRECATED, use uniform_end """
    return safestring.mark_safe('</form>')

@register.filter(name='uniform')
def uniform_formrendering(form, submitText=None):
    if not isinstance(form, forms.Form) and not isinstance(form, forms.ModelForm):
        raise IncompatibleFormError()

    render = uniform_startrendering(form)
    render += uniform_form_rendering(form, submitText)
    render += uniform_endrendering(form)

    return safestring.mark_safe(render)

@register.inclusion_tag('forms/begin.html')
def uniform_begin(form=None):
    return {'form': form}

@register.inclusion_tag('forms/end.html')
def uniform_end():
    return {}

@register.inclusion_tag('forms/submit.html')
def uniform_submit(label):
    return {'label' : label}

@register.inclusion_tag('forms/headers.html')
def uniform_header():
        return {'MEDIA_URL' : settings.MEDIA_URL}

def get_input(item, args={ }, is_child=False):
    if isinstance(item.field.widget, (forms.RadioSelect,)):
        return UniformInputRadio(item, args=args, is_child=is_child)
    elif isinstance(item.field.widget, (forms.TextInput,)) and hasattr(item.field, 'choices'):
        return UniformInputSelectbox(item, args=args, is_child=is_child)
    elif isinstance(item.field.widget, (forms.Select,)):
        return UniformInputSelectbox(item, args=args, is_child=is_child)
    elif isinstance(item.field.widget, (forms.TextInput, forms.PasswordInput)):
        return UniformInputText(item, args=args, is_child=is_child)
    elif isinstance(item.field.widget, (forms.CheckboxInput)):
        return UniformInputCheckbox(item, args=args, is_child=is_child)
    elif isinstance(item.field.widget, (forms.Textarea)):
        return UniformInputTextarea(item, args=args, is_child=is_child)
    elif isinstance(item.field.widget, (forms.FileInput)):
        return UniformInputFile(item, args=args, is_child=is_child)
    else:
        return '<div style="color: red">ERROR: UNKNOWN INPUT TYPE %s</div>\n' % item.name

def render_Submit(text):
    return '<fieldset class="inlineLabels"><div class="buttonHolder"><button type="submit" class="submitButton">%s</button></div></fieldset>' % text