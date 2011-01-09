from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group, User

from selvbetjening.notify.htdigest.models import CompatiblePassword, HTDigestFile, filter_username

class Command(BaseCommand):
    help = 'Generate htdigest files'

    def handle(self, *args, **options):
        for htdigestfile in HTDigestFile.objects.all():

            users = User.objects.filter(groups__in=htdigestfile.groups.all()) \
                                .exclude(htdigest_passwd=None)

            lines = ['%s:%s:%s' % (filter_username(user.username),
                                   settings.NOTIFY_HTDIGEST_REALM,
                                   user.htdigest_passwd.password)
                     for user in users]

            content = '\n'.join(lines)

            fp = open(htdigestfile.file_path, 'w')
            fp.write(content)
            fp.close()
