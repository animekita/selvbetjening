
Backbone.LayoutManager.configure({
    fetch: function (path){
        return Handlebars.compile($(path).html());
    },
    render: function(template, context) {
        return template(context);
    }
});


$(function() {

    var attendees = new Attendees(window.attendee_data);
    var event = new Event(window.event_data);

    var application = new Application({
        eventModel: event,
        attendeesCollection: attendees
    });
    application.startStateMachine({currentState: 'init'});

    $("body").html(application.el);
    application.render();

    var router = new Router();

    router.on('route:attendees', function() {
        application.trigger('findAttendee');
    });

    router.on('route:attendee', function(attendeeId) {
        application.trigger('selectAttendee', attendeeId);
    });

    attendees.on('selected', function(attendeeModel) {
        application.trigger('selectAttendee', attendeeModel.get('id'));
    });

    Backbone.history.start();
});

