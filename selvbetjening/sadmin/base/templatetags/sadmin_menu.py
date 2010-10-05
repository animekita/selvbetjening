from django import template

from selvbetjening.sadmin.base.nav import registry, OptionProxy

register = template.Library()

@register.tag(name='get_menu')
def get_menu(parser, token):
    try:
        tag_name, menu_id, delimiter, target_var = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, \
              "%r tag requires arguments in the format menu_id as var" % \
              token.contents.split()[0]

    return MenuGetter(menu_id, target_var)

class MenuGetter(template.Node):
    def __init__(self, menu_id, target_var):
        self.menu_id = menu_id
        self.target_var = target_var

    def render(self, context):
        try:
            context[self.target_var] = \
                   [OptionProxy(element, context) for element in registry[self.menu_id]]
        except KeyError:
            context[self.target_var] = None

        return ''