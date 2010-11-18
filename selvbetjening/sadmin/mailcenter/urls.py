from django.conf.urls.defaults import patterns, url

url_patterns = patterns('selvbetjening.sadmin.mailcenter.views',
    url(r'^email/(?P<email_pk>[0-9]+)/filter/$', 'filter_email', name='mailcenter_email_filter'),
    url(r'^email/(?P<email_pk>[0-9]+)/preview/$', 'preview_email', name='mailcenter_email_preview'),
    url(r'^email/(?P<email_pk>[0-9]+)/send/$', 'send_email', name='mailcenter_email_send'),
    url(r'^email/(?P<email_pk>[0-9]+)/bind/$', 'bind_email', name='mailcenter_email_bind'),
    url(r'^email/(?P<email_pk>[0-9]+)/$', 'update_email', name='mailcenter_email_update'),
    url(r'^create/$', 'update_email', name='mailcenter_emails_create'),

    url(r'^$', 'list_emails', name='mailcenter_emails_list'),
)