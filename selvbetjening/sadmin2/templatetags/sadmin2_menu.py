
from django import template
from django.core.urlresolvers import reverse

register = template.Library()


@register.simple_tag(takes_context=True)
def sadmin2_emit_name(context, menu_item):

    if 'name' in menu_item:
        return menu_item['name']

    return menu_item['name_callback'](context)


@register.simple_tag(takes_context=True)
def sadmin2_emit_url(context, menu_item):

    if 'url' in menu_item:
        return reverse(menu_item['url'])

    if 'url_callback' in menu_item:
        return menu_item['url_callback'](context)

    return '#'