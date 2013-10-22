from crispy_forms.layout import HTML
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.utils.translation import ugettext as _
from core.events.models.options import AutoSelectChoiceOption, DiscountOption

from selvbetjening.core.events.models import SubOption, Option

from selvbetjening.frontend.utilities.forms import *


def _get_type_html(type_raw):
    return """
<div class="form-group">
<label class="control-label col-lg-2">Type</label>
<div class="controls col-lg-8">%s</div>
</div>""" % unicode(type_raw).title()


class OptionForm(forms.ModelForm):

    class Meta:
        model = Option
        fields = ('name', 'description', 'price')

        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        type = kwargs.pop('type')

        super(OptionForm, self).__init__(*args, **kwargs)

        self.helper = S2FormHelper(horizontal=True)

        layout = S2Layout(S2Fieldset(
            None,
            'name',
            HTML(_get_type_html(type)),
            'description',
            'price'))

        self.helper.add_layout(layout)
        self.helper.form_tag = False


class AutoSelectChoiceOptionForm(forms.ModelForm):

    class Meta:
        model = AutoSelectChoiceOption
        fields = ('name', 'description', 'price', 'auto_select_suboption')

        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        type = kwargs.pop('type')

        super(AutoSelectChoiceOptionForm, self).__init__(*args, **kwargs)

        if 'instance' in kwargs:
            option_pk = kwargs['instance'].pk
        else:
            option_pk = 0

        self.fields['auto_select_suboption'].queryset = SubOption.objects.filter(option__pk=option_pk)

        self.helper = S2FormHelper(horizontal=True)

        layout = S2Layout(S2Fieldset(
            None,
            'name',
            HTML(_get_type_html(type)),
            'description',
            'price',
            'auto_select_suboption'))

        self.helper.add_layout(layout)
        self.helper.form_tag = False


class DiscountOptionForm(forms.ModelForm):

    class Meta:
        model = DiscountOption
        fields = 'name', 'discount_suboption'

    def __init__(self, *args, **kwargs):
        super(DiscountOptionForm, self).__init__(*args, **kwargs)

        if 'instance' in kwargs:
            option_pk = kwargs['instance'].pk
        else:
            option_pk = 0

        self.fields['discount_suboption'].queryset = SubOption.objects.filter(option__pk=option_pk)

        self.helper = S2FormHelper(horizontal=True)

        layout = S2Layout(S2Fieldset(None, 'name', HTML(_get_type_html('discount')), 'discount_suboption'))

        self.helper.add_layout(layout)
        self.helper.form_tag = False


class SubOptionForm(forms.ModelForm):

    name = forms.CharField(max_length=255, required=False)


class SubOptionInlineFormset(BaseInlineFormSet):

    helper = S2FormHelper(horizontal=True)

    layout = S2Layout(
        S2Fieldset(None,
                   'name', 'price', 'DELETE'))

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