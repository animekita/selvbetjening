
import logging

from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
from django.forms.widgets import Input
from django.template.defaultfilters import floatformat
from django.utils.translation import ugettext as _

from selvbetjening.core.events.models.options import AutoSelectChoiceOption, DiscountOption, DiscountCode
from selvbetjening.core.events.models import Selection
from selvbetjening.core.events.options.scope import SCOPE

logger = logging.getLogger('selvbetjening.events')


class BaseWidget(object):

    def __init__(self, scope, option, send_notifications=False):
        self.scope = scope
        self.option = option
        self.send_notifications = send_notifications
        self.required = self.option.required if self.scope != SCOPE.SADMIN else False
        self.use_native_required = self.required and self.option.depends_on is None  # if we have a dependency, then disable native required checks

    def is_editable(self, attendee):
        return True

    def clean_callback(self, value):

        if (value in validators.EMPTY_VALUES or not value) and self.required:
            raise ValidationError(_('This field is required.'))

        return value if value is not None else False

    def _log_change(self, action, selection, attendee):

        text = ''
        if selection.text is not None and len(selection.text) > 0:
            text = ' -- %s' % selection.text

        logger.info('Selection %s (%s @ %s,-)%s', action, unicode(selection), selection.price, text,
                    extra={
                        'related_user': attendee.user,
                        'related_attendee': attendee
                    })


class BooleanWidget(BaseWidget):

    def get_field(self, attrs=None):

        field = forms.BooleanField(
            label=self.option.name if self.option.price == 0 else '%s (%s,-)' % (self.option.name, floatformat(self.option.price, "-2")),
            required=self.use_native_required,
            help_text=self.option.description,
            widget=forms.CheckboxInput(attrs=attrs))
        field.render_as_required = self.required
        return field

    def save_callback(self, attendee, value):

        if value is not None and value:
            selection, created = Selection.objects.get_or_create(
                option_id=self.option.pk,
                attendee=attendee
            )

            if created and self.send_notifications:
                self.option.send_notification_on_select(attendee)

            if created:
                self._log_change('created', selection, attendee)

        else:
            try:
                selection = Selection.objects.get(
                    option_id=self.option.pk,
                    attendee=attendee
                )

                self._log_change('deleted', selection, attendee)

                selection.delete()
            except Selection.DoesNotExist:
                pass

    def initial_value(self, selection):
        return True


class TextWidget(BaseWidget):

    def get_field(self, attrs=None):

        field = forms.CharField(
            label=self.option.name,
            required=self.use_native_required,
            help_text=self.option.description,
            widget=forms.TextInput(attrs=attrs))
        field.render_as_required = self.required
        return field

    def save_callback(self, attendee, value):

        if value is not None and len(value.strip()) > 0:
            value = value.strip()

            selection, created = Selection.objects.get_or_create(
                option_id=self.option.pk,
                attendee=attendee,
                defaults={
                    'text': value
                }
            )

            if created and self.send_notifications:
                self.option.send_notification_on_select(attendee)

            if created:
                self._log_change('created', selection, attendee)
            elif selection.text != value:
                selection.text = value
                selection.save()
                self._log_change('changed', selection, attendee)

        else:
            try:
                selection = Selection.objects.get(
                    option_id=self.option.pk,
                    attendee=attendee
                )

                selection.delete()

                self._log_change('deleted', selection, attendee)
            except Selection.DoesNotExist:
                pass

    def initial_value(self, selection):
        return selection.text


class ChoiceWidget(BaseWidget):

    def __init__(self, scope, option, send_notifications=False):
        super(ChoiceWidget, self).__init__(scope, option, send_notifications=send_notifications)

        self.choices = [('', '')] + [('suboption_%s' % suboption.pk, self._label(suboption))
                                     for suboption in self.option.suboptions.all()]

    def get_field(self, attrs=None):

        field = forms.ChoiceField(
            label=self.option.name,
            required=self.use_native_required,
            help_text=self.option.description,
            widget=forms.Select(attrs=attrs),
            choices=self.choices)
        field.render_as_required = self.required
        return field

    def save_callback(self, attendee, value):

        if value is not None and len(value) > 0:

            _, pk = value.split('_')

            selection, created = Selection.objects.get_or_create(
                option_id=self.option.pk,
                attendee=attendee,
                defaults={
                    'suboption_id': pk
                }
            )

            if created and self.send_notifications:
                self.option.send_notification_on_select(attendee)

            if created:
                self._log_change('created', selection, attendee)
            elif selection.suboption_id != pk:
                selection.suboption_id = pk
                selection.save()
                self._log_change('changed', selection, attendee)

        else:
            try:
                selection = Selection.objects.get(
                    option_id=self.option.pk,
                    attendee=attendee
                )

                selection.delete()

                self._log_change('deleted', selection, attendee)
            except Selection.DoesNotExist:
                pass

    def clean_callback(self, value):
        value = super(ChoiceWidget, self).clean_callback(value)

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
        return suboption.name if price == 0 else '%s (%s)' % (suboption.name, floatformat(price, "-2"))


class AutoSelectBooleanWidget(BooleanWidget):

    def get_field(self, attrs=None):
        return forms.BooleanField(
            required=False,
            widget=forms.HiddenInput(attrs=None))

    def clean_callback(self, value):
        return True

    def initial_value(self, selection):
        return True


class AutoChoiceDisplay(Input):

    CANT_DISABLE = True

    def __init__(self, suboption, *args, **kwargs):
        self.suboption = suboption
        super(AutoChoiceDisplay, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        value = self.suboption.name if self.suboption.real_price == 0 else '%s (%s,-)' % (self.suboption.name, floatformat(self.suboption.real_price, "-2"))
        return '<p class="form-control-static">%s</p>' % value


class AutoSelectChoiceWidget(ChoiceWidget):

    def __init__(self, *args, **kwargs):
        super(AutoSelectChoiceWidget, self).__init__(*args, **kwargs)
        self.option = AutoSelectChoiceOption.objects.get(option_ptr=self.option)

    def get_field(self, attrs=None):

        field = forms.ChoiceField(
            label=self.option.name,
            required=self.use_native_required,
            widget=AutoChoiceDisplay(self.option.auto_select_suboption, attrs=attrs),
            choices=self.choices)
        field.render_as_native = self.required
        return field

    def save_callback(self, attendee, value):

        selection, created = Selection.objects.get_or_create(
            option_id=self.option.pk,
            attendee=attendee,
            defaults={
                'suboption': self.option.auto_select_suboption
            }
        )

        if created and self.send_notifications:
            self.option.send_notification_on_select(attendee)

        if created:
            self._log_change('created', selection, attendee)
        elif selection.suboption != self.option.auto_select_suboption:
            selection.suboption = self.option.auto_select_suboption
            selection.save()
            self._log_change('changed', selection, attendee)


class DiscountWidget(TextWidget):

    def __init__(self, scope, option, send_notifications=False):
        super(DiscountWidget, self).__init__(scope, option, send_notifications=send_notifications)
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

            if created and self.send_notifications:
                self.option.send_notification_on_select(attendee)

            if created:
                self._log_change('created', selection, attendee)

    def clean_callback(self, value):
        value = super(DiscountWidget, self).clean_callback(value)

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