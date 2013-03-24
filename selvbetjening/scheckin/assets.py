import os

from django_assets import Bundle, register

css = Bundle(
    'contrib/bootstrap/css/bootstrap.min.css',
    'contrib/bootstrap/css/bootstrap-responsive.min.css',
    'css/branding.css',
    'scheckin/css/scheckin.css',
    filters='cssmin',
    output='gen/scheckin.min.css'
)

register('scheckin_css', css)

js = Bundle(
    'scheckin/js/libs/jquery/jquery.js',
    'scheckin/js/libs/jquery/jquery.blockUI.js',
    'scheckin/js/libs/jquery/jquery.highlight.js',

    'scheckin/js/libs/underscore/underscore.js',

    'scheckin/js/libs/backbone/backbone.js',
    'scheckin/js/libs/backbone/backbone.layoutmanager.js',
    'scheckin/js/libs/backbone/backbone.mutators.js',
    'scheckin/js/libs/backbone/backbone.tastypie.js',

    'scheckin/js/libs/handlebars/handlebars.js',

    'scheckin/js/views/attendee-comment.js',
    'scheckin/js/views/attendee-comments.js',
    'scheckin/js/views/attendees-list.js',
    'scheckin/js/views/attendees-list-item.js',
    'scheckin/js/views/attendee-page.js',
    'scheckin/js/views/attendee-selection-group.js',
    'scheckin/js/views/attendee-selection-option.js',
    'scheckin/js/views/attendee-selection.js',
    'scheckin/js/views/attendee-payments.js',
    'scheckin/js/views/attendee-state.js',
    'scheckin/js/views/attendees-page.js',

    'scheckin/js/models.js',
    'scheckin/js/router.js',
    'scheckin/js/app.js',
    'scheckin/js/main.js',

    filters='jsmin',
    output='gen/scheckin.min.js'
)

register('scheckin_js', js)