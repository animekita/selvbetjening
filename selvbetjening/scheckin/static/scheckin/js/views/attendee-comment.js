var AttendeeCommentView = Backbone.LayoutView.extend({
    template: '#attendee-comment-item-template',
    tagName: 'tr',

    commentModel: null,

    initialize: function(options) {
        this.commentModel = options.commentModel;
    },

    serialize: function() {
        return {
            comment: this.commentModel.toJSON()
        };
    }

});
