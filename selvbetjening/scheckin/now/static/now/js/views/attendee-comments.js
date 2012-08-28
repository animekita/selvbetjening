
var AttendeeCommentsView = Backbone.LayoutView.extend({
    template: '#attendee-comment-template',

    commentCollection: null,
    attendeeModel: null,

    events: {
        'click .doComment': 'addCommentHandler'
    },

    initialize: function(options) {
        this.commentCollection = options.commentCollection;
        this.commentCollection.on('reset', function() { this.render(); }, this);

        this.attendeeModel = options.attendeeModel;
    },

    beforeRender: function() {

        this.commentCollection.each(function(commentModel) {
            this.insertView('table', new AttendeeCommentView({
                commentModel: commentModel
            }));

        }, this);

    },

    addCommentHandler: function(e) {
        e.stopImmediatePropagation();
        e.preventDefault();

        var user = 'sema';

        var comment = new Comment({
            author: user,
            comment: this.$('textarea').val(),
            attendee: this.attendeeModel.get('resource_uri')
        });

        var that = this;
        comment.save({
            success: function() { this.commentCollection.fetch(); }
        });
    }
});
