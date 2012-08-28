
var AttendeeSelectionView = Backbone.LayoutView.extend({
    template: "#attendee-selection-template",

    eventModel: null,
    attendeeModel: null,
    selectionCollection: null,

    initialize: function(options) {
        this.eventModel = options.eventModel;
        this.eventModel.on('change', this.render, this);

        this.selectionCollection = options.selectionCollection;
        this.attendeeModel = options.attendeeModel;
    },

    cleanup: function(options) {
        this.eventModel.off('change', this.render, this);
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