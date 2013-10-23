from crispy_forms.layout import HTML
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.utils.translation import ugettext as _

from selvbetjening.core.events.models.options import AutoSelectChoiceOption, DiscountOption
from selvbetjening.core.events.models import SubOption, Option

from selvbetjening.frontend.utilities.forms import *


def _get_type_html(type_raw):
    return """
<div class="form-group">
<label class="control-label col-lg-2">Type</label>
<div class="controls col-lg-8">%s</div>
</div>""" % unicode(type_raw).title()


def _get_price_html(price):
    return """
<div class="form-group">
<label class="control-label col-lg-2">Price</label>
<div class="controls col-lg-8">%s</div>
</div>""" % price


def _field_filter(field, type_raw, instance):
    if field == 'type':
        return HTML(_get_type_html(type_raw))

    if field == 'price' and instance is not None:
        return HTML(_get_price_html(instance.price))

    return field


def option_form_factory(db_model, db_fields, layout_fields, type_raw, post_super_callback=None):

    class OptionForm(forms.ModelForm):

        class Meta:
            model = db_model
            fields = db_fields

            widgets = {
                'description': forms.Textarea(attrs={'rows': 2}),
            }

        def __init__(self, *args, **kwargs):
            super(OptionForm, self).__init__(*args, **kwargs)

            if post_super_callback is not None:
                post_super_callback(self, *args, **kwargs)

            instance = kwargs.get('instance', None)
            fields = [_field_filter(field, type_raw, instance) for field in layout_fields]

            self.helper = S2FormHelper(horizontal=True)

            layout = S2Layout(S2Fieldset(
                None,
                *fields))

            self.helper.add_layout(layout)
            self.helper.form_tag = False

        def save(self, *args, **kwargs):
            commit = kwargs.get('commit', True)
            kwargs['commit'] = False

            instance = super(OptionForm, self).save(*args, **kwargs)
            instance.type = type_raw

            if commit:
                instance.save()

            return instance

    return OptionForm


def _auto_select_choice_post_super_callback(form, *args, **kwargs):
    if 'instance' in kwargs:
        option_pk = kwargs['instance'].pk
    else:
        option_pk = 0

    form.fields['auto_select_suboption'].queryset = SubOption.objects.filter(option__pk=option_pk)

UpdateAutoSelectChoiceOptionForm = option_form_factory(
    AutoSelectChoiceOption,
    ('name', 'description', 'auto_select_suboption'),
    ('name', 'type', 'description', 'price', 'auto_select_suboption'),
    'autoselectchoice',
    post_super_callback=_auto_select_choice_post_super_callback
)

CreateAutoSelectChoiceOptionForm = option_form_factory(
    AutoSelectChoiceOption,
    ('name', 'description', 'price'),
    ('name', 'type', 'description', 'price'),
    'autoselectchoice',
)


def _discount_post_super_callback(form, *args, **kwargs):
    if 'instance' in kwargs:
        option_pk = kwargs['instance'].pk
    else:
        option_pk = 0

    form.fields['discount_suboption'].queryset = SubOption.objects.filter(option__pk=option_pk)


UpdateDiscountOptionForm = option_form_factory(
    DiscountOption,
    ('name', 'description', 'discount_suboption'),
    ('name', 'type', 'description', 'discount_suboption'),
    'discount',
    post_super_callback=_discount_post_super_callback
)

CreateDiscountOptionForm = option_form_factory(
    DiscountOption,
    ('name', 'description'),
    ('name', 'type', 'description'),
    'discount'
)


class SubOptionForm(forms.ModelForm):

    name = forms.CharField(max_length=255, required=False)


class SubOptionInlineFormset(BaseInlineFormSet):

    helper = S2FormHelper(horizontal=True)

    layout = S2Layout(
        S2Fieldset(None,
                   'name', 'price'))

    helper.add_layout(layout)
    helper.form_tag = False

SubOptionFormset = inlineformset_factory(Option, SubOption, formset=SubOptionInlineFormset, form=SubOptionForm)


class GenerateDiscountCodes(forms.Form):

    prefix = forms.CharField(max_length=4)
    amount = forms.IntegerField()

    helper = S2FormHelper(horizontal=True)

    layout = S2Layout(
        S2Fieldset(None,
                   'prefix', 'amount'))

    helper.add_layout(layout)
    helper.add_input(S2SubmitCreate(name='gen'))