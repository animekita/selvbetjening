from selenium.common.exceptions import WebDriverException
from splinter import Browser
import urlparse

from django.core.urlresolvers import reverse
from django.test import LiveServerTestCase


class UITestCase(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        try:
            cls.wd = Browser('phantomjs')
        except WebDriverException:
            cls.wd = Browser()  # fall back to the default (firefox) if phantomjs is unavailable

        super(UITestCase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.wd.quit()
        super(UITestCase, cls).tearDownClass()

    def open(self, url):
        self.wd.visit(urlparse.urljoin(self.live_server_url, url))

    def login_admin(self):
        self.open(reverse('sadmin2:dashboard'))

        self.wd.fill('username', 'admin')
        self.wd.fill('password', 'admin')

        self.wd.find_by_name('login').first.click()
        self.wd.is_element_not_present_by_name('login', wait_time=10)  # wait for the page to start reloading
