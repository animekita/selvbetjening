from django.core.urlresolvers import reverse
from common import UITestCase


class DashboardTestCase(UITestCase):

    fixtures = ['sdemo-example-site.json']

    def test_load(self):

        self.login_admin()

        # Check that the dashboard is the first page we see after login
        self.assertTrue(self.wd.is_text_present('Dashboard'))
