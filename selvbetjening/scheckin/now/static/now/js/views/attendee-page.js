
var AttendeePage = Backbone.LayoutView.extend({
    template: "#attendee-page-template",

    attendeeModel: null,
    eventModel: null,
    selectionCollection: null,
    commentCollection: null,

    events: {
        'click .doBack' : 'backHandler'
    },

    initialize: function(options) {

        this.attendeeModel = new Attendee({
            id: options.attendeeId
        });
        this.attendeeModel.on('change', this.render, this);
        this.attendeeModel.fetch();

        this.eventModel = new Event({
            id: options.eventId
        });
        this.eventModel.fetch();

        this.selectionCollection = new Selections();
        this.selectionCollection.fetch({
            data: {
                attendee: options.attendeeId
            }
        });

        this.commentCollection = new Comments();
        this.commentCollection.fetch({
            data: {
                attendee: options.attendeeId
            }
        });

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
            selectionCollection: this.selectionCollection
        })).render();

        this.setView('.attendeeComments', new AttendeeCommentsView({
            commentCollection: this.commentCollection,
            attendeeModel: this.attendeeModel
        })).render();
    },

    backHandler: function() {
        this.trigger('doneEditing');
    }

});