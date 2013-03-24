
var AttendeeListItemView = Backbone.Layout.extend({
    template: '#attendees-list-item-template',
    tagName: 'tr',

    attendeeModel: null,

    events: {
        'click' : 'selectAttendeeHandler'
    },

    initialize: function(options) {
        this.attendeeModel = options.attendeeModel;
        this.attendeeModel.on("change", this.render, this);
        this.attendeeModel.on('show', this.showHandler, this);
        this.attendeeModel.on('hide', this.hideHandler, this);
    },

    cleanup: function() {
        this.attendeeModel.off("change", this.render, this);
    },

    serialize: function() {
        return {
            attendee: this.attendeeModel.toJSON()
        };
    },

    selectAttendeeHandler: function() {
        this.attendeeModel.trigger('selected', this.attendeeModel);
    },

    showHandler: function(highlightQuery) {
        this.$el.show();

        if (highlightQuery) {
            this.$(".field").removeHighlight();
            this.$(".field").highlight(highlightQuery);
        }
    },

    hideHandler: function() {
        this.$(".field").removeHighlight();
        this.$el.hide();
    }

});
