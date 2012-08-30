
var AttendeeSelectionGroupView = Backbone.LayoutView.extend({
    template: "#attendee-selection-group-template",

    optionGroup: null,
    attendeeModel: null,
    selectionCollection: null,

    initialize: function(options) {
        this.optionGroup = options.optionGroup;
        this.attendeeModel = options.attendeeModel;

        this.selectionCollection = options.selectionCollection;
        this.selectionCollection.on('reset', this.render, this);
    },

    cleanup: function() {
        this.selectionCollection.off('reset', this.render, this);
    },

    serialize: function() {
        return {
            optionGroup: this.optionGroup
        }
    },

    beforeRender: function() {

        _.each(this.optionGroup.options, function(option) {

            var selectionModel = this.selectionCollection.find(function(selection) {
                return selection.get('option') == option.resource_uri;
            }, this);

            if (selectionModel == null) {
                selectionModel = new Selection({
                    attendee: this.attendeeModel.get('resource_uri'),
                    option: option.resource_uri
                });
            }

            selectionModel.on('change', function() { this.attendeeModel.fetch(); }, this);

            this.insertView('.control-group', new AttendeeSelectionOptionView({
                option: option,
                selectionModel: selectionModel,
                attendeeModel: this.attendeeModel
            }));

        }, this);
    }
});
