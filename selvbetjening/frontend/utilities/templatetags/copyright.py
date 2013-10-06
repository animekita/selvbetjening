import datetime

from django import template

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

