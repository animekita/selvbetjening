from django import template
from django import newforms as forms
from django.utils import safestring
from django.conf import settings

register = template.Library()

@register.filter(name='uniform')
def uniform_formrendering(form, submitText):
    render = '<form method="POST" action="" class="uniForm">\n\n'

    if form.non_field_errors():
        render += '<div id="errorMsg">\n'
        render += form.non_field_errors().as_ul()
        render += '</div>\n'
    
    if hasattr(form, 'Meta'):
        for section in form.Meta.layout:
            render += '<fieldset class="inlineLabels"><legend>' + section[0] + '</legend>\n'
            for item_name in section[1]:
                render += render_input(form[item_name])
            render += '</fieldset>\n'
            
    else:
        render += '<fieldset class="inlineLabels">'
        for item in form:
            render += render_input(item)
        render += '</fieldset>\n'
    
    render += render_Submit(submitText)
    
    return safestring.mark_safe(render + '</form>')

@register.tag
def uniform_header(parser, token):
        return UniformHeaderNode()

class UniformHeaderNode(template.Node):
    
        def render(self, context):
                return safestring.mark_safe('<link rel="stylesheet" type="text/css" href="%scss/uni-form.css">\n<script type="text/javascript" src="%sjs/datepicker.js"></script>\n<link href="%scss/datepicker.css" rel="stylesheet" type="text/css" />' % 
                                            (settings.MEDIA_URL, settings.MEDIA_URL, settings.MEDIA_URL))

def render_input(item):
    
    if isinstance(item.field.widget, (forms.TextInput, forms.PasswordInput)):
        return render_TextInput(item)
    elif isinstance(item.field.widget, (forms.CheckboxInput)):
        return render_Checkbox(item)
    else:
        return '<div style="color: red">ERROR: UNKNOWN INPUT TYPE %s</div>\n' % item.name

def render_TextInput(field):
    render = ''
    
    if field.errors:
        error = ' error'
        errormsg = '<p class="errorField"><strong>' + field.errors.as_text() + '</strong></p>\n'
    else:
        error = ''
        errormsg = ''

    if field.field.required == True:
        render += field.label_tag('<em>*</em> ' + field.label) + '\n'
    else:
        render += field.label_tag() + '\n'
     
    attrs = {'class' : 'textInput text'}

    if isinstance(field.field, forms.DateField):
        attrs['class'] += ' w8em format-d-m-y divider-dash highlight-days-67'
    
    render += field.as_widget(attrs=attrs) + '\n'
    
    
    
    if field.help_text:
        render += '<p class="formHint">' + field.help_text + '</p>\n'
    
    return '<div class="ctrlHolder%s">\n' % error + errormsg + render + '</div>\n\n'

def render_Checkbox(field):
    render = ""
    
    if field.errors:
        error = ' error'
        errormsg = '<p class="errorField"><strong>' + field.errors.as_text() + '</strong></p>\n'
    else:
        error = ''
        errormsg = ''
   
    if field.field.required == True:
        render += field.label_tag(field.as_widget() + " <em>*</em> " + field.label) + '\n'
    else:
        render += field.label_tag(field.as_widget() + field.label) + '\n'

    return '<div class="ctrlHolder%s">\n' % error + errormsg + "<div>" + render + '</div></div>\n\n'

def render_Submit(text):
    return '<fieldset class="inlineLabels"><div class="buttonHolder"><button type="submit" class="submitButton">%s</button></div></fieldset>' % text