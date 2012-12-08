# coding=UTF-8
from django.forms.widgets import RadioSelect
import re

from django.template import Context
from django.conf import settings
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.utils.encoding import smart_str

from countries.models import Country
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, HTML

from selvbetjening.viewbase.forms.helpers import SFieldset

from models import UserProfile, UserCommunication, UserWebsite
from shortcuts import get_or_create_profile
import signals

username_re = re.compile("^[a-zA-Z0-9_]+$")

def validate_username(username):
    if not username_re.match(username):
        raise forms.ValidationError(_(u'Usernames can only contain letters, numbers and underscores'))

    try:
        User.objects.get(username__exact=username)
    except User.DoesNotExist:
        return username

    raise forms.ValidationError(_(u'This username is already taken. Please choose another.'))

class UsernameField(forms.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 30
        kwargs['widget'] = forms.TextInput()
        kwargs['label'] = _(u"Username")
        kwargs['help_text'] = _(u"Your username can only contain the characters a-z, underscore and numbers.")

        super(UsernameField, self).__init__(*args, **kwargs)

class LazyCountryChoices(object):
    """
    Defer database interaction such that database initialisation works.
    """
    def __iter__(self):
        if not hasattr(self, 'cache'):
            self.cache = [(country.pk, str(country)) for country in Country.objects.only('printable_name')]
        return iter(self.cache)

class BaseProfileForm(forms.Form):
    COUNTRY_CHOICES = LazyCountryChoices()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)

        if self.user is not None:
            initial = kwargs.get('initial', {})
            initial.update(self._build_initial())

            kwargs['initial'] = initial

        super(BaseProfileForm, self).__init__(*args, **kwargs)

        # defer database interactrion such that database initialisation works
        self.fields['country'].choices = self.COUNTRY_CHOICES

    first_name = forms.CharField(max_length=50,
                          widget=forms.TextInput(),
                          label=_(u'First name'),
                          required=True)

    last_name = forms.CharField(max_length=50,
                          widget=forms.TextInput(),
                          label=_(u'Last name'),
                          required=True)

    email = forms.EmailField(max_length=75, label=_(u'E-mail'))

    dateofbirth = forms.DateField(label=_(u'Date of birth'),
                                  help_text=_(u'Use the date format dd.mm.yyyy'),
                                  input_formats=['%d.%m.%Y'])

    street = forms.CharField(max_length=50,
                             widget=forms.TextInput(),
                             label=_(u'Street'),
                             required=False)
    postalcode = forms.IntegerField(label=_(u'Postal code'), required=False)

    city = forms.CharField(max_length=255,
                           widget=forms.TextInput(),
                           label=_(u'City'),
                           required=False)

    country = forms.ChoiceField(label=_(u'Country'),
                                required=False, initial='DK',)

    phonenumber = forms.RegexField(label=_(u'Phonenumber'), required=False,
                                   regex=r'(\+[0-9]{2}( )?)?([0-9]{8})')

    send_me_email = forms.BooleanField(widget=forms.CheckboxInput(),
                             label=_(u'Inform me about events and other important changes.'),
                             initial=True, required=False)

    sex = forms.ChoiceField(label=_(u'Sex'),
                            choices=UserProfile.SEX,
                            required=False,
                            widget=RadioSelect)

    def _build_initial(self):
        user_profile = get_or_create_profile(self.user)

        initial = {'first_name' : self.user.first_name,
                   'last_name' : self.user.last_name,
                   'dateofbirth' : user_profile.dateofbirth,
                   'street' : user_profile.street,
                   'city' : user_profile.city,
                   'postalcode' : user_profile.postalcode,
                   'phonenumber' : user_profile.phonenumber,
                   'email' : self.user.email,
                   'sex' : user_profile.sex,
                   'send_me_email' : user_profile.send_me_email,
                   'country' : user_profile.country.pk,
                   }

        return initial

    def clean_dateofbirth(self):
        # The birth year must be above 1900 to be compatible with strftime
        if self.cleaned_data['dateofbirth'].year < 1900:
            raise forms.ValidationError(_(u'Your birthday is not allowed to be dated before 1900'))

        return self.cleaned_data['dateofbirth']

    def clean_country(self):
        try:
            country = Country.objects.get(pk=self.cleaned_data['country'])

            return country
        except Country.DoesNotExist:
            raise forms.ValidationError(_(u'Invalid country selected'))

    def save(self, user=None):
        """
        Update user profile and user records
        """
        if user is None:
            user = self.user

        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.save()

        profile = get_or_create_profile(user)

        profile.dateofbirth = self.cleaned_data['dateofbirth']
        profile.street = self.cleaned_data['street']
        profile.postalcode = self.cleaned_data['postalcode']
        profile.city = self.cleaned_data['city']
        profile.country = self.cleaned_data['country']
        profile.phonenumber = self.cleaned_data['phonenumber']
        profile.send_me_email = self.cleaned_data['send_me_email']
        profile.sex = self.cleaned_data['sex']
        profile.save()

class ProfileForm(BaseProfileForm):
    COMMUNICATION_FIELDNAME = 'usercommunication_%s'
    WEBSITE_NAME_FIELDNAME = 'userwebsite_name_%s'
    WEBSITE_URL_FIELDNAME = 'userwebsite_url_%s'

    def __init__(self, user, *args, **kwargs):
        initial = kwargs.get('initial', {})

        communications = UserCommunication.objects.filter(user=user)
        for communication in communications:
            field_name = ProfileForm.COMMUNICATION_FIELDNAME % communication.method

            initial[field_name] = communication.identification

        for website in UserWebsite.objects.filter(user=user):
            name_field = ProfileForm.WEBSITE_NAME_FIELDNAME % website.pk
            url_field = ProfileForm.WEBSITE_URL_FIELDNAME % website.pk

            initial[name_field] = website.name
            initial[url_field] = website.url

        kwargs['initial'] = initial
        kwargs['user'] = user

        super(ProfileForm, self).__init__(*args, **kwargs)

        if len(args) > 0:
            post = args[0]
            self._build_new_websites(post)

        methods = self._build_communication()
        websites = self._build_websites()

        layout = Layout(SFieldset(_(u'Basic Information'),
                                       Row('first_name', 'last_name'), 'dateofbirth', 'sex',),
                        SFieldset(_(u'Address'),
                                       'street', Row('postalcode', 'city'), 'country'),
                        SFieldset(_(u'Contact Information'),
                                       'phonenumber', 'email', 'send_me_email',
                                       *methods),
                        SFieldset(_(u'Your Homepages (shown on your profile)'), *websites))

        submit = Submit(_('Change personal information'),
                        _('Change personal information'))

        self.helper = FormHelper()
        self.helper.add_input(submit)
        self.helper.add_layout(layout)

    def _build_communication(self):
        methods = []
        for method, method_name in UserCommunication.METHOD_CHOICES:
            field_name = self.COMMUNICATION_FIELDNAME % method

            self.fields[field_name] = \
                forms.CharField(max_length=255,
                                label=method_name,
                                required=False)

            methods.append(field_name)

        return methods

    def _add_website_fields(self, form, name_field, url_field):
        form.fields[name_field] = forms.CharField(max_length=32,
                                                      required=False,
                                                      label=_(u'Name'))

        form.fields[url_field] = forms.URLField(required=False,
                                                label=_(u'URL'))

    def _build_new_websites(self, post):
        self.new_website_keys = []

        for data_key in post:
            if self.WEBSITE_NAME_FIELDNAME % 'new' in data_key:
                try:
                    new_id = data_key[len(self.WEBSITE_NAME_FIELDNAME) + 2 : -1]
                    new_id = int(new_id)
                except:
                    continue

                key = 'new[%s]' % new_id
                self.new_website_keys.append(key)

                name_field = self.WEBSITE_NAME_FIELDNAME % key
                url_field = self.WEBSITE_URL_FIELDNAME % key

                self._add_website_fields(self, name_field, url_field)

    def _build_websites(self):
        websites = []

        for website in UserWebsite.objects.filter(user=self.user):
            name_field = ProfileForm.WEBSITE_NAME_FIELDNAME % website.pk
            url_field = ProfileForm.WEBSITE_URL_FIELDNAME % website.pk

            self._add_website_fields(self, name_field, url_field)

            websites.append(Row(name_field, url_field))

        link_text = _(u'Add website')
        add_url = '%sgraphics/icons/add.png' % settings.STATIC_URL


        template_field_name = self.WEBSITE_NAME_FIELDNAME % 'new[ELEMENT_ID]'
        template_field_url = self.WEBSITE_URL_FIELDNAME % 'new[ELEMENT_ID]'

        template_form = forms.Form()
        self._add_website_fields(template_form,
                                 template_field_name,
                                 template_field_url)
        template_form.rendered_fields = set()

        template_row = Row(template_field_name, template_field_url).render(template_form, 'default', Context())
        template_row = template_row.replace("\n", '')

        html = """
        <script type="text/javascript">
        var counter = 0
        var template = '%s';

        function addWebsiteElement(element) {

        new_element = template.replace(/ELEMENT_ID/g, counter);
        counter++;

        $('fieldset .ctrlHolder').last().before(new_element);

        }
        </script>

        <div class="ctrlHolder">
        <img src="%s" /> <a href="javascript:void(0);" onclick="return addWebsiteElement(this);">%s</a>
        </div>
        """

        websites.append(HTML(html % (template_row, add_url, unicode(link_text))))

        return websites

    def save(self):
        super(ProfileForm, self).save()

        user = self.user

        for method, method_name in UserCommunication.METHOD_CHOICES:
            field_name = self.COMMUNICATION_FIELDNAME % method

            identification = self.cleaned_data.get(field_name, '')

            try:
                user_communication = UserCommunication.objects.get(user=user,
                                                                   method=method)

                if identification == '':
                    user_communication.delete()
                else:
                    user_communication.identification = identification
                    user_communication.save()

            except UserCommunication.DoesNotExist:
                if identification != '':
                    UserCommunication.objects.create(user=user,
                                                     method=method,
                                                     identification=identification)

        for website in UserWebsite.objects.filter(user=user):
            name_field = self.WEBSITE_NAME_FIELDNAME % website.pk
            url_field = self.WEBSITE_URL_FIELDNAME % website.pk

            name_value = self.cleaned_data.get(name_field, '')
            url_value = self.cleaned_data.get(url_field, '')

            if name_value != '' and url_value != '':
                website.name = name_value
                website.url = url_value
                website.save()
            else:
                website.delete()

        for key in getattr(self, 'new_website_keys', []):
            name_field = self.WEBSITE_NAME_FIELDNAME % key
            url_field = self.WEBSITE_URL_FIELDNAME % key

            name_value = self.cleaned_data.get(name_field, '')
            url_value = self.cleaned_data.get(url_field, '')

            if name_value != '' and url_value != '':
                UserWebsite.objects.create(user=user,
                                           name=name_value,
                                           url=url_value)

class RegistrationForm(BaseProfileForm):
    """ Form for registering a new user account. """

    username = UsernameField()
    password1 = forms.CharField(widget=forms.PasswordInput(),
                                label=_(u"Password"))
    password2 = forms.CharField(widget=forms.PasswordInput(),
                                label=_(u"Verify password"))

    tos = forms.BooleanField(widget=forms.CheckboxInput(),
                             label=_(u"I allow the storage of my personal information on this site."))

    layout = Layout(SFieldset(_(u"Personal Information"),
                             'first_name', 'last_name', 'dateofbirth', 'sex', 'phonenumber', 'email', 'send_me_email'),
                    SFieldset(_(u"Address"),
                             'street', 'postalcode', 'city', 'country'),
                    SFieldset(_(u"User"),
                             'username', 'password1', 'password2'),
                    SFieldset(_(u"Data management terms"),
                             'tos'))

    helper = FormHelper()

    submit = Submit(_('Create user'), _('Create user'))
    helper.add_input(submit)
    helper.use_csrf_protection = True
    helper.add_layout(layout)

    def clean_tos(self):
        if not self.cleaned_data.get('tos', False):
            raise forms.ValidationError(_(u"You must allow us to store your information to create an account."))

        return self.cleaned_data['tos']

    def clean_username(self):
        """ Validates that the username is alphanumeric and is not in use. """

        return validate_username(self.cleaned_data['username'])

    def clean_password2(self):
        """ Validates that the two password inputs match. """

        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_(u"You must type the same password each time"))

            return self.cleaned_data['password2']

        return ''

    def save(self):
        user = User.objects.create_user(self.cleaned_data['username'],
                                        self.cleaned_data['email'],
                                        self.cleaned_data['password1'])

        user.is_active = True
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()

        UserProfile.objects.create(user=user,
                                   dateofbirth=self.cleaned_data['dateofbirth'],
                                   city=self.cleaned_data['city'],
                                   street=self.cleaned_data['street'],
                                   postalcode=self.cleaned_data['postalcode'],
                                   phonenumber=self.cleaned_data['phonenumber'],
                                   send_me_email=self.cleaned_data['send_me_email'],
                                   sex=self.cleaned_data['sex'],)

        signals.user_created.send(sender=self,
                                  instance=user,
                                  clear_text_password=smart_str(self.cleaned_data["password1"]))

        return user

class AdminSelectMigrationUsers(forms.Form):
    old_user = forms.IntegerField(label=_('Old user account'))
    new_user = forms.IntegerField(label=_('New user account'))

    def clean(self):
        try:
            if self.cleaned_data['old_user'] == self.cleaned_data['new_user']:
                raise forms.ValidationError(_('Old user account and new user account must be different'))

        except KeyError:
            pass # if old_user or new_user is not set, then another error should have shown itself

        return self.cleaned_data

