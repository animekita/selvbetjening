
var AttendeePage = Backbone.Layout.extend({
    template: "#attendee-page-template",

    eventModel: null,
    attendeeModel: null,
    commentCollection: null,
    attendeeId: null,

    events: {
        'click .doBack' : function() {
            this.trigger('doneEditing');
        }
    },

    initialize: function(options) {

        this.eventModel = options.eventModel;

        this.attendeeModel = new Attendee({
            id: options.attendeeId
        });
        this.attendeeModel.on('change', this.render, this);
        this.attendeeModel.fetch();

        this.attendeeId = options.attendeeId;
    },

    serialize: function() {
        return {
            attendee: this.attendeeModel.toJSON()
        };
    },

    beforeRender: function() {
        this.setView('.attendeeState', new AttendeeStateView({
            eventModel: this.eventModel,
            attendeeModel: this.attendeeModel
        })).render();

        this.setView('.attendeeSelection', new AttendeeSelectionView({
            eventModel: this.eventModel,
            attendeeModel: this.attendeeModel,
            attendeeId: this.attendeeId
        })).render();

        this.setView('.attendeeComments', new AttendeeCommentsView({
            attendeeModel: this.attendeeModel
        })).render();
    }

});