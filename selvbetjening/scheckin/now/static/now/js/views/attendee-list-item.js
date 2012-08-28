
var AttendeeListItemView = Backbone.LayoutView.extend({
    template: '#attendee-list-item-template',
    tagName: 'tr',

    attendeeModel: null,

    events: {
        'click .doSelectAttendee' : 'selectAttendeeHandler'
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

    showHandler: function() {
        this.$el.show();
    },

    hideHandler: function() {
        this.$el.hide();
    }

});
