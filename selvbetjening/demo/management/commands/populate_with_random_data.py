
from django.core.management.base import NoArgsCommand
from django.conf import settings

from selvbetjening.core.user.models import SUser
from selvbetjening.core.events.models import Event, Group, Attend, OptionGroup, Option, Selection

import autofixture
from autofixture import generators


class EventAutoFixture(autofixture.AutoFixture):
    field_values = {
        'title': generators.LoremSentenceGenerator(max_length=30)
    }

autofixture.register(Event, EventAutoFixture)


class GroupAutoFixture(autofixture.AutoFixture):
    field_values = {
        'name': generators.LoremWordGenerator(max_length=10)
    }

autofixture.register(Group, GroupAutoFixture)


class Command(NoArgsCommand):

    def handle_noargs(self, **options):

        if not settings.DEBUG:
            print """Population of database with random data is not supported for producting sites. ' \

                  'Please set settings.DEBUG to True"""
            return

        confirmation = raw_input("""You have requested the demo site to populate your database with random data.

You should NEVER do this on a production site.

Are you sure you want to do this?

    Type 'yes' to continue, or 'no' to cancel: """)

        if confirmation != "yes":
            print '\nDatabase population cancelled'
            return

        self.populate_database()

    def populate_database(self):

        autofixture.create(SUser, 200)

        autofixture.create(Group, 1)
        autofixture.create(Event, 3)
        autofixture.create(OptionGroup, 10)
        autofixture.create(Option, 30)

        autofixture.create(Attend, 300)
        autofixture.create(Selection, 500)



