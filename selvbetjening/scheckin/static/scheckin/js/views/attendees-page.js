
var AttendeesPage = Backbone.Layout.extend({
    template: "#attendees-page-template",

    events:{
        'keyup input': 'inputChanged'
    },

    eventModel: null,
    attendeesCollection: null,

    highlightTainted: false,

    initialize: function(options) {

        this.eventModel = options.eventModel;
        this.attendeesCollection = options.attendeesCollection;

    },

    beforeRender: function() {

        this.setView('.attendee-list', new AttendeeListView({
            eventModel: this.eventModel,
            attendeesCollection: this.attendeesCollection
        })).render();

    },

    inputChanged: function() {
        var q = this.$('input')[0].value.toLowerCase();

        var doHighlight = q.length >= 3;

        if (this.highlightTainted && !doHighlight) {
            this.$el.removeHighlight();
        }

        this.highlightTainted = doHighlight;

        if (q == '') {

            if (this.highlightMode) {
                this.$el.removeHighlight();
                this.highlightMode = false;
            }

            this.attendeesCollection.each(function(attendeeModel) {
                attendeeModel.trigger('show');
            });

        } else {

            this.attendeesCollection.each(function(attendeeModel) {
                var user = attendeeModel.get('user');

                if (user.username.toLowerCase().indexOf(q) != -1 ||
                    user.name.toLowerCase().indexOf(q) != -1 ||
                    user.email.toLowerCase().indexOf(q) != -1) {

                    attendeeModel.trigger('show', doHighlight ? q : null);
                } else {
                    attendeeModel.trigger('hide');
                }

            });

        }
    }

});
