
var AttendeesPage = Backbone.LayoutView.extend({
    template: "#attendees-page-template",

    events:{
        'keyup input': 'inputChanged'
    },

    eventModel: null,
    attendeesCollection: null,

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
        var q = this.$('input').attr('value').toLowerCase();

        if (q == '') {

            this.attendeesCollection.each(function(attendeeModel) {

                attendeeModel.trigger('show');

            });

        } else {

            this.attendeesCollection.each(function(attendeeModel) {
                var user = attendeeModel.get('user');

                if (user.username.toLowerCase().indexOf(q) != -1 ||
                    user.name.toLowerCase().indexOf(q) != -1 ||
                    user.email.toLowerCase().indexOf(q) != -1) {

                    attendeeModel.trigger('show');

                } else {

                    attendeeModel.trigger('hide');

                }

            });

        }
    }

});
