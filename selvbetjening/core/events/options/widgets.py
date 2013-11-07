
from django import forms
from django.core.exceptions import ValidationError
from django.forms.widgets import Input
from django.utils.translation import ugettext as _

from selvbetjening.core.events.models.options import AutoSelectChoiceOption, DiscountOption, DiscountCode
from selvbetjening.core.events.models import Selection
from selvbetjening.core.events.options.scope import SCOPE


class BaseWidget(object):

    def is_editable(self, attendee):
        return True


class BooleanWidget(BaseWidget):

    def __init__(self, scope, option):
        self.scope = scope
        self.option = option

    def get_field(self):

        return forms.BooleanField(
            label=self.option.name if self.option.price == 0 else '%s (%s,-)' % (self.option.name, self.option.price),
            required=self.option.required if self.scope != SCOPE.SADMIN else False,
            help_text=self.option.description,
            widget=forms.CheckboxInput())

    def save_callback(self, attendee, value):

        if value is not None and value:
            Selection.objects.get_or_create(
                option_id=self.option.pk,
                attendee=attendee
            )
        else:
            Selection.objects.filter(
                option_id=self.option.pk,
                attendee=attendee
            ).delete()

    def clean_callback(self, value):
        return value if value is not None else False

    def initial_value(self, selection):
        return True


class TextWidget(BaseWidget):

    def __init__(self, scope, option):
        self.scope = scope
        self.option = option

    def get_field(self):

        return forms.CharField(
            label=self.option.name,
            required=self.option.required if self.scope != SCOPE.SADMIN else False,
            help_text=self.option.description,
            widget=forms.TextInput())

    def save_callback(self, attendee, value):

        if value is not None and len(value.strip()) > 0:
            selection, created = Selection.objects.get_or_create(
                option_id=self.option.pk,
                attendee=attendee
            )

            selection.text = value.strip()
            selection.save()
        else:
            Selection.objects.filter(
                option_id=self.option.pk,
                attendee=attendee
            ).delete()

    def clean_callback(self, value):
        return value

    def initial_value(self, selection):
        return selection.text


class ChoiceWidget(BaseWidget):

    def __init__(self, scope, option):
        self.scope = scope
        self.option = option

        self.choices = [('', '')] + [('suboption_%s' % suboption.pk, self._label(suboption))
                                     for suboption in self.option.suboptions.all()]

    def get_field(self):

        return forms.ChoiceField(
            label=self.option.name,
            required=self.option.required if self.scope != SCOPE.SADMIN else False,
            help_text=self.option.description,
            widget=forms.Select(),
            choices=self.choices)

    def save_callback(self, attendee, value):

        if value is not None and len(value) > 0:
            selection, created = Selection.objects.get_or_create(
                option_id=self.option.pk,
                attendee=attendee
            )

            _, pk = value.split('_')

            selection.suboption_id = pk
            selection.save()

        else:
            Selection.objects.filter(
                option_id=self.option.pk,
                attendee=attendee
            ).delete()

    def clean_callback(self, value):

        if value is None:
            return None

        for choice in self.choices:
            if value == choice[0]:
                return value

        raise ValidationError(_('Choice %s is not allowed') % value)

    def initial_value(self, selection):
        if selection.suboption is not None:
            return 'suboption_%s' % selection.suboption.pk
        else:
            return None

    def _label(self, suboption):
        price = suboption.real_price
        return suboption.name if price == 0 else '%s (%s)' % (suboption.name, price)


class AutoSelectBooleanWidget(BooleanWidget):

    def get_field(self):
        return forms.BooleanField(
            required=False,
            widget=forms.HiddenInput())

    def clean_callback(self, value):
        return True

    def initial_value(self, selection):
        return True


class AutoChoiceDisplay(Input):

    CANT_DISABLE = True

    def __init__(self, scope, suboption):
        self.scope = scope
        self.suboption = suboption
        super(AutoChoiceDisplay, self).__init__()

    def render(self, name, value, attrs=None):
        value = self.suboption.name if self.suboption.real_price == 0 else '%s (%s,-)' % (self.suboption.name, self.suboption.real_price)
        return '<p class="form-control-static">%s</p>' % value


class AutoSelectChoiceWidget(ChoiceWidget):

    def __init__(self, *args, **kwargs):
        super(AutoSelectChoiceWidget, self).__init__(*args, **kwargs)
        self.option = AutoSelectChoiceOption.objects.get(option_ptr=self.option)

    def get_field(self):

        return forms.ChoiceField(
            label=self.option.name,
            required=self.option.required if self.scope != SCOPE.SADMIN else False,
            widget=AutoChoiceDisplay(self.option.auto_select_suboption),
            choices=self.choices)

    def save_callback(self, attendee, value):

        selection, created = Selection.objects.get_or_create(
            option_id=self.option.pk,
            attendee=attendee
        )

        selection.suboption = self.option.auto_select_suboption
        selection.save()


class DiscountWidget(TextWidget):

    def __init__(self, scope, option):
        super(DiscountWidget, self).__init__(scope, option)
        self.discount_option = DiscountOption.objects.get(option_ptr=option)

    def is_editable(self, attendee):
        return not Selection.objects.filter(option=self.option, attendee=attendee).exists()

    def save_callback(self, attendee, value):

        if value is not None:

            discountoption = DiscountOption.objects.get(option_ptr=self.option)

            suboption = {}

            if discountoption.discount_suboption is not None:
                suboption = {'suboption': discountoption.discount_suboption}

            selection, created = Selection.objects.get_or_create(
                option=self.option,
                attendee=attendee,
                **suboption
            )

            value.selection = selection
            value.save()

    def clean_callback(self, value):

        if value is None or len(value) == 0:
            return None

        try:
            code = DiscountCode.objects.get(
                discount_option=self.option,
                code=value,
                selection=None
            )

            return code

        except DiscountCode.DoesNotExist:
            raise ValidationError(_('Discount code not valid'))

    def initial_value(self, selection):

        try:
            code = DiscountCode.objects.get(selection=selection)
            return code.code
        except DiscountCode.DoesNotExist:
            return ''