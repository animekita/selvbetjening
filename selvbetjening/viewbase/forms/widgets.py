import datetime
import re

from django.utils.translation import ugettext_lazy as _
from django.forms.widgets import Widget, Select
from django.utils.dates import MONTHS
from django.utils.safestring import mark_safe
from django.forms.extras import SelectDateWidget
from django.utils.translation import get_language

__all__ = ('UniformSelectDateWidget',)

RE_DATE = re.compile(r'(\d{4})-(\d\d?)-(\d\d?)$')

class UniformSelectDateWidget(SelectDateWidget):
    """
    Reworked version of the django distributed SelectedDateWidget
    """

    def render(self, name, value, attrs=None):
        try:
            year_val, month_val, day_val = value.year, value.month, value.day
        except AttributeError:
            year_val = month_val = day_val = None
            if isinstance(value, basestring):
                match = RE_DATE.match(value)
                if match:
                    year_val, month_val, day_val = [int(v) for v in match.groups()]

        output = []

        output.append('<div class="multiField">')

        if 'id' in self.attrs:
            id_ = self.attrs['id']
        else:
            id_ = 'id_%s' % name

        month = []
        month_choices = MONTHS.items()
        if not (self.required and value):
            month_choices.append(self.none_value)
        month_choices.sort()
        local_attrs = self.build_attrs(id=self.month_field % id_)
        s = Select(choices=month_choices)
        select_html = s.render(self.month_field % name, month_val, local_attrs)
        month.append('<label for="id_%(name)s" class="blockLabel">%(label)s ' % {'name' : self.month_field % name,
                                                                                  'label' : unicode(_(u'Month'))})
        month.append(select_html)
        month.append('</label>')

        day = []
        day_choices = [(i, i) for i in range(1, 32)]
        if not (self.required and value):
            day_choices.insert(0, self.none_value)
        local_attrs['id'] = self.day_field % id_
        s = Select(choices=day_choices)
        select_html = s.render(self.day_field % name, day_val, local_attrs)
        day.append('<label for="id_%(name)s" class="blockLabel">%(label)s ' % {'name' : self.day_field % name,
                                                                                  'label' : unicode(_(u'Day'))})
        day.append(select_html)
        day.append('</label>')

        if get_language() == 'da-dk':
            output.extend(day)
            output.extend(month)
        else:
            output.extend(month)
            output.extend(day)

        year_choices = [(i, i) for i in self.years]
        if not (self.required and value):
            year_choices.insert(0, self.none_value)
        local_attrs['id'] = self.year_field % id_
        s = Select(choices=year_choices)
        select_html = s.render(self.year_field % name, year_val, local_attrs)
        output.append('<label for="id_%(name)s" class="blockLabel">%(label)s ' % {'name' : self.year_field % name,
                                                                                  'label' : unicode(_(u'Year'))})
        output.append(select_html)
        output.append('</label>')

        output.append('</div>')

        return mark_safe(u'\n'.join(output))

    def id_for_label(self, id_):
        return '%s_month' % id_
    id_for_label = classmethod(id_for_label)

    def value_from_datadict(self, data, files, name):
        y = data.get(self.year_field % name)
        m = data.get(self.month_field % name)
        d = data.get(self.day_field % name)
        if y == m == d == "0":
            return None
        if y and m and d:
            return '%s-%s-%s' % (y, m, d)
        return data.get(name, None)
