
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

    initialize: function(options) {
        this.eventModel = options.eventModel;
        this.attendeesCollection = options.attendeesCollection;
    },

    checkinHandler: function(attendeeId) {
        var attendeePage = new AttendeePage({
            eventModel: this.eventModel,
            attendeeId: attendeeId
        });

        attendeePage.on('doneEditing', function() {
            this.trigger('findAttendee');
        }, this);

        this.setView("#main-view", attendeePage).render();
    },

    searchHandler: function() {
        this.setView("#main-view", new AttendeesPage({
            eventModel: this.eventModel,
            attendeesCollection: this.attendeesCollection
        })).render();
    }

}, Backbone.StateMachine, Backbone.Events));
