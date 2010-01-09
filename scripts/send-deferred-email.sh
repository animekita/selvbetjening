#!/bin/sh

WORKON_PATH=/PATH/TO/.virtualenvs/PROJECT
PROJECT_ROOT=/PATH/TO/PROJECT/ROOT/
MAIL_LOG=$PROJECT_ROOT/logs/cron_mail.log

# activate virtual environment
. $WORKON_PATH/bin/activate

cd $PROJECT_ROOT
python manage.py retry_deferred >> $MAIL_LOG 2>&1