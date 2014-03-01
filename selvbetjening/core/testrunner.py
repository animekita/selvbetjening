from django.test.simple import DjangoTestSuiteRunner
from django.conf import settings

INCLUDING_APPS = getattr(settings, 'TEST_INCLUDE', [])


class IncludingTestSuiteRunner(DjangoTestSuiteRunner):

    def build_suite(self, *args, **kwargs):
        suite = super(IncludingTestSuiteRunner, self).build_suite(*args, **kwargs)

        tests = []
        for case in suite:
            pkg = case.__class__.__module__.split('.')[0]
            if pkg in INCLUDING_APPS:
                tests.append(case)
        suite._tests = tests

        return suite

    def setup_test_environment(self, **kwargs):
        super(IncludingTestSuiteRunner, self).setup_test_environment(**kwargs)
        settings.STATICFILES_STORAGE='pipeline.storage.NonPackagingPipelineStorage'

