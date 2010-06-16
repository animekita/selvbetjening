from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from selvbetjening.core.selvadmin.admin import site

# initialize admin site
import selvbetjening.data.members.admin
import selvbetjening.data.events.admin
import selvbetjening.data.invoice.admin
import selvbetjening.clients.mailcenter.admin
import selvbetjening.notify.concrete5.admin