from django.test import TestCase

from templatetags import uniform as uniformtags

class UniformTagsTestCase(TestCase):

    def test_non_form_evaluation(self):
        class InvalidForm(object):
            pass

        self.assertRaises(uniformtags.IncompatibleFormError,
                          uniformtags.uniform_formrendering, InvalidForm(), '')