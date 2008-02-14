import datetime

from django import template
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.translation import ugettext as _

from accounting.models import MembershipState

register = template.Library()

@register.tag
def copyright_time(parser, token):
        try:
                # split_contents() knows not to split quoted strings.
                tag_name, format_string = token.split_contents()
        except ValueError:
                raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents.split()[0]
        if int(format_string) == 0:
                raise template.TemplateSyntaxError, "%r tag's argument should be an integer" % tag_name
        return CopyrightTimeNode(int(format_string))

class CopyrightTimeNode(template.Node):
        def __init__(self, time):
                self.time = time
        
        def render(self, context):
                if datetime.date.today().year == self.time:
                        return self.time
                else:
                        return str(self.time) + " - " + str(datetime.date.today().year)

@register.tag
def icon_link(parser, token):
        content = token.split_contents()
        
        return IconLinkNode(*content[1:])

class IconLinkNode(template.Node):
        def __init__(self, help_text, icon_name, page_name, *page_attrs):
                self.page_name = page_name
                self.icon_name = icon_name
                self.help_text = help_text
                self.page_attrs = [template.Variable(val) for val in page_attrs]
        
        def render(self, context):
                attrs = [x.resolve(context) for x in self.page_attrs]
                return '<a class="icon" href="' + reverse(self.page_name, args=attrs) + '" title="' + self.help_text.replace('"', '') + '"><img src="' + settings.MEDIA_URL + 'images/icons/' + self.icon_name + '.png" /></a>'
   
@register.tag
def icon(parser, token):
        content = token.split_contents()
        
        return IconNode(*content[1:])

class IconNode(template.Node):
        def __init__(self, alt_text, icon_name, title):
                self.alt_text = alt_text
                self.icon_name = icon_name
                self.title = title
        
        def render(self, context):
                return '<img class="icon" src="' + settings.MEDIA_URL + 'images/icons/' + self.icon_name + '.png" title="' + self.title + '" alt="' + self.alt_text.replace('"', '') + '"/>'
        

@register.filter(name='translate')
def translate(text, category):
        if category == "membership_state":
                if text == MembershipState.ACTIVE:
                        return _('Active member')
                elif text == MembershipState.CONDITIONAL_ACTIVE:
                        return _('Conditional active member')
                elif text == MembershipState.PASSIVE:
                        return _('Passive member')
                elif text == MembershipState.INACTIVE:
                        return _('Inactive member')
        
        elif category == "payment_type":
                if text == "FULL":
                        return _('Full payment')
                elif text == "FRATE":
                        return _('First rate')
                elif text == "SRATE":
                        return _('Second rate')