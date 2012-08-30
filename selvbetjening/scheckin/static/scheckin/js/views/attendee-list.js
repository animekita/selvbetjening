
var AttendeeListView = Backbone.LayoutView.extend({
    template: "#attendee-list-template",

    attendeesCollection: null,

    initialize: function(options) {
        this.attendeesCollection = options.attendeesCollection;
        this.attendeesCollection.on('reset', this.render, this);
    },

    beforeRender: function() {

        this.attendeesCollection.each(function(attendeeModel) {

            this.insertView('tbody', new AttendeeListItemView({
                attendeeModel: attendeeModel
            }));

        }, this);
    }

});