
var AttendeeSelectionView = Backbone.Layout.extend({
    template: "#attendee-selection-template",

    eventModel: null,
    attendeeModel: null,
    selectionCollection: null,

    initialize: function(options) {
        this.eventModel = options.eventModel;
        this.eventModel.on('change', this.render, this);

        this.attendeeModel = options.attendeeModel;

        this.selectionCollection = new Selections();
        this.selectionCollection.fetch({
            data: {
                attendee: options.attendeeId,
                limit: 0
            },
            reset: true
        });
    },

    beforeRender: function() {

        _.each(this.eventModel.get('option_groups'), function(optionGroup) {
            this.insertView('form', new AttendeeSelectionGroupView({
                optionGroup: optionGroup,
                attendeeModel: this.attendeeModel,
                selectionCollection: this.selectionCollection
            }));
        }, this);

    }
});