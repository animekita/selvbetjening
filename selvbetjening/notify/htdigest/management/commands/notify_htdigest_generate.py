from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from selvbetjening.notify.htdigest.models import HTDigestFile, filter_username

class Command(BaseCommand):
    help = 'Generate htdigest files'

    def handle(self, *args, **options):
        if ':' in settings.NOTIFY_HTDIGEST_REALM:
            raise ValueError('Illegal escape character in NOTIFY_HTDIGEST_REALM setting')

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
