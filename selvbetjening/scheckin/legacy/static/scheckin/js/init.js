
var ApplicationRouter = Backbone.Router.extend({

    routes: {
        "": "attendees",
        "attendee/:attendeeId/" : "attendee"
    }

});

var Application = Backbone.Layout.extend(_.extend({
    template: "#chrome-layout",

    states: {
        init: {},
        search: {enterCb: ['searchHandler']},
        checkin: {enterCb: ['checkinHandler']}
    },

    transitions: {
        init: {
            findAttendee: {enterState: 'search'},
            selectAttendee: {enterState: 'checkin'}
        },
        search: {
            selectAttendee: {enterState: 'checkin'}
        },
        checkin: {
            findAttendee: {enterState: 'search'}
        }
    },

    checkinHandler: function(attendeeId) {
        var attendeePage = new AttendeePage({
            eventModel: window.event,
            attendeeId: attendeeId
        });

        attendeePage.on('doneEditing', function() {
            this.trigger('findAttendee');
        }, this);

        this.setView("#main-view", attendeePage).render();
    },

    searchHandler: function() {
        this.setView("#main-view", new AttendeesPage({
            eventModel: window.event,
            attendeesCollection: window.attendees
        })).render();
    }

}, Backbone.StateMachine, Backbone.Events));

Backbone.LayoutManager.configure({
    fetch: function (path){
        return Handlebars.compile($(path).html());
    },
    render: function(template, context) {
        return template(context);
    }
});

$(function() {

    var application = new Application();
    application.startStateMachine({currentState: 'init'});

    $("body").html(application.el);
    application.render();

    var router = new ApplicationRouter();

    router.on('route:attendees', function() {
        application.trigger('findAttendee');
    });

    router.on('route:attendee', function(attendeeId) {
        application.trigger('selectAttendee', attendeeId);
    });

    window.attendees.on('selected', function(attendeeModel) {
        application.trigger('selectAttendee', attendeeModel.get('id'));
    });

    Backbone.history.start();
});
