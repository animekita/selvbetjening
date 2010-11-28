from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from selvbetjening.core.selvadmin.admin import site

# initialize admin site
import selvbetjening.core.members.admin
import selvbetjening.core.events.admin
import selvbetjening.core.invoice.admin
import selvbetjening.core.logger.admin
import selvbetjening.notify.concrete5.admin