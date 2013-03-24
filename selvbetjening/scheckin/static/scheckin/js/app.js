
var Application = Backbone.Layout.extend(_.extend({
    template: "#chrome-layout",

    initialize: function(options) {
        this.eventModel = options.eventModel;
        this.attendeesCollection = options.attendeesCollection;
    },

    serialize: function() {
        return {
            eventTitle: this.eventModel.get('title')
        }
    },

    displayCheckInHandler: function(attendeeId) {
        var attendeePage = new AttendeePage({
            eventModel: this.eventModel,
            attendeeId: attendeeId
        });

        attendeePage.on('doneEditing', function() {
            this.displaySearchHandler();
        }, this);

        this.setView("#main-view", attendeePage).render();
    },

    displaySearchHandler: function() {
        this.setView("#main-view", new AttendeesPage({
            eventModel: this.eventModel,
            attendeesCollection: this.attendeesCollection
        })).render();
    }

}, Backbone.Events));
