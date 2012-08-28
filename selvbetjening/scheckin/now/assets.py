import os

from django_assets import Bundle, register

css = Bundle(
    'contrib/bootstrap/css/bootstrap.min.css',
    'contrib/bootstrap/css/bootstrap-responsive.min.css',
    'css/branding.css',
    'now/css/now.css',
    filters='cssmin',
    output='gen/now.min.css'
)

register('now_css', css)

js = Bundle(
    'now/js/libs/jquery/jquery.js',
    'now/js/libs/jquery/jquery.blockUI.js',

    'now/js/libs/underscore/underscore.js',

    'now/js/libs/backbone/backbone.js',
    'now/js/libs/backbone/backbone.layoutmanager.js',
    'now/js/libs/backbone/backbone.mutators.js',
    'now/js/libs/backbone/backbone.statemachine.js',
    'now/js/libs/backbone/backbone.tastypie.js',

    'now/js/libs/handlebars/handlebars.js',

    'now/js/views/attendee-comment.js',
    'now/js/views/attendee-comments.js',
    'now/js/views/attendee-list.js',
    'now/js/views/attendee-list-item.js',
    'now/js/views/attendee-page.js',
    'now/js/views/attendee-selection-group.js',
    'now/js/views/attendee-selection-option.js',
    'now/js/views/attendee-selection.js',
    'now/js/views/attendee-state.js',
    'now/js/views/attendees-page.js',

    'now/js/models.js',
    'now/js/router.js',
    'now/js/app.js',
    'now/js/main.js',

    filters='jsmin',
    output='gen/now.min.js'
)

register('now_js', js)