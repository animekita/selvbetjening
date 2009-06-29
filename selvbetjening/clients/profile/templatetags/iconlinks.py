from django import template
from django.core.urlresolvers import reverse
from django.conf import settings

register = template.Library()

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
