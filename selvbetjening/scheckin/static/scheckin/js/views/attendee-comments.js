
var AttendeeCommentsView = Backbone.Layout.extend({
    template: '#attendee-comment-template',

    commentCollection: null,
    attendeeModel: null,

    events: {
        'submit .commentForm': 'addCommentHandler'
    },

    initialize: function(options) {
        this.attendeeModel = options.attendeeModel;

        this.commentCollection = new Comments();
        this.commentCollection.on('reset', this.render, this);
        this.commentCollection.on('add', this.render, this);
        this.commentCollection.on('remove', this.render, this);
        this.commentCollection.fetch({
            data: {
                attendee: options.attendeeModel.attendeeId
            },
            reset: true
        });
    },

    beforeRender: function() {
        this.commentCollection.each(function(commentModel) {
            this.insertView('table', new AttendeeCommentView({
                commentModel: commentModel
            }));

        }, this);

    },

    addCommentHandler: function(e) {

        e.stopPropagation();
        e.preventDefault();

        var user = 'check-in';

        var comment = new Comment({
            author: user,
            comment: this.$('textarea').val(),
            attendee: this.attendeeModel.get('resource_uri')
        });

        var that = this;
        comment.save({}, {
            success: function() {
                console.log("aaaaaaaaaaa");
                that.commentCollection.add(comment);
                that.$('textarea').val("");
            }
        });
    }
});
