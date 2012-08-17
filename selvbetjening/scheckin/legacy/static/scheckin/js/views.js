
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

var AttendeeListView = Backbone.LayoutView.extend({
    template: "#attendee-list-template",

    attendeesCollection: null,

    initialize: function(options) {
        this.attendeesCollection = options.attendeesCollection;
        this.attendeesCollection.on('reset', this.render, this);
    },
    
    beforeRender: function() {
        console.log('render');

        this.attendeesCollection.each(function(attendeeModel) {

            this.insertView('tbody', new AttendeeListItemView({
                attendeeModel: attendeeModel
            }));

        }, this);
    }

});

var AttendeesPage = Backbone.LayoutView.extend({
    template: "#attendees-page-template",

    events:{
        'keyup input': 'inputChanged'
    },

    eventModel: null,
    attendeesCollection: null,

    initialize: function(options) {

        this.eventModel = options.eventModel;
        this.attendeesCollection = options.attendeesCollection;

    },

    beforeRender: function() {

        this.setView('.attendee-list', new AttendeeListView({
            eventModel: this.eventModel,
            attendeesCollection: this.attendeesCollection
        })).render();

    },

    inputChanged: function() {
        var q = this.$('input').attr('value').toLowerCase();

        if (q == '') {

            this.attendeesCollection.each(function(attendeeModel) {

                attendeeModel.trigger('show');

            });

        } else {

            this.attendeesCollection.each(function(attendeeModel) {
                var user = attendeeModel.get('user');

                if (user.username.toLowerCase().indexOf(q) != -1 ||
                    user.name.toLowerCase().indexOf(q) != -1 ||
                    user.email.toLowerCase().indexOf(q) != -1) {

                    attendeeModel.trigger('show');

                } else {

                    attendeeModel.trigger('hide');

                }

            });

        }
    }

});

var AttendeeSelectionOptionView = Backbone.LayoutView.extend({
    template: "#attendee-selection-option-template",
    tagName: "div",
    className: "controls",

    option: null,
    selectionModel: null,
    attendeeModel: null,

    modelChecked: null,

    events: {
        'change input': 'selectionChangedHandler'
    },

    initialize: function(options) {

        this.option = options.option;
        this.selectionModel = options.selectionModel;
        this.attendeeModel = options.attendeeModel;

        this.modelChecked = !this.selectionModel.isNew();
    },

    serialize: function() {
        return {
            option: this.option,
            isChecked: this.modelChecked
        };
    },

    selectionChangedHandler: function() {

        var checked = this.$('input:checkbox').attr('checked') == "checked";

        if (checked != this.modelChecked) {

            if (checked) {
                // add it

                this.selectionModel.save();
                this.modelChecked = true;

            } else {
                // delete it

                this.selectionModel.destroy({
                    success: function(model) {
                        model.unset('id');
                        model.unset('resource_uri');
                    }
                });

                this.modelChecked = false;
            }

        }
    },

    afterRender: function() {
        this.$('input:checkbox').attr('checked', this.modelChecked);
    }
});

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

var AttendeeStateView = Backbone.LayoutView.extend({
    template: "#attendee-state-template",

    attendeeModel: null,
    eventModel: null,

    editStatusMode: false,

    events: {
        'click .doCheckIn': 'checkInHandler',
        'click .doPay': 'payHandler',
        'click .doToggleEdit': 'toggleEditHandler',
        'click .doSave': 'saveHandler',
        'submit form': 'saveHandler'
    },

    initialize: function(options) {
        this.attendeeModel = options.attendeeModel;
        this.attendeeModel.on('change', this.render, this);

        this.eventModel = options.eventModel;
    },

    serialize: function() {
        return {
            attendee: this.attendeeModel.toJSON(),
            editStatusMode: this.editStatusMode
        };
    },

    afterRender: function() {
        if (this.editStatusMode == true) {
            this.$('#paymentAmount').focus();
        }
    },

    toggleEditHandler: function() {
        this.editStatusMode = !this.editStatusMode;
        this.render();
    },

    enterSavingMode: function() {
        this.$('.attendeeForm').block({
            message: "Gemmer...",
            css: {
                border: 'none',
                padding: '15px',
                backgroundColor: '#000',
                '-webkit-border-radius': '10px',
                '-moz-border-radius': '10px',
                opacity: .5,
                color: '#fff'
            },
            overlayCSS: {
                backgroundColor: null
            }
        });
    },

    checkInHandler: function() {

        this.enterSavingMode();

        this.attendeeModel.set('state', 'attended');

        var that = this;
        this.attendeeModel.save().done(function() {
            that.attendeeModel.fetch().done(function() {
                that.render();
            });
        });
    },

    payHandler: function() {

        this.enterSavingMode();

        var payment = new Payment({
            amount: this.attendeeModel.get('paymentDue'),
            note: "Automatic payment through nem check-in",
            invoice: this.attendeeModel.get('invoice').resource_uri
        });

        var that = this;
        payment.save().done(function() {
            that.attendeeModel.fetch().done(function() {
                that.render();
            });
        });
    },

    saveHandler: function(e) {
        e.stopImmediatePropagation();
        e.preventDefault();

        var that = this;
        this.enterSavingMode();

        this.attendeeModel.set('state', this.$('form[name=attendeeForm] input:radio[name=state]:checked').val());

        var paymentAmount = this.$('form[name=attendeeForm] input:text[name=paymentAmount]').val();

        if (paymentAmount != undefined) {

            paymentAmount = parseFloat(paymentAmount.replace(',', '.'));

            if (paymentAmount != 0 && !isNaN(paymentAmount)) {

                var payment = new Payment({
                    amount: paymentAmount,
                    note: "Automatic payment through nem check-in",
                    invoice: this.attendeeModel.get('invoice').resource_uri
                });

                this.attendeeModel.get('invoice').total_paid += paymentAmount;

                payment.save().done(function() {
                    that.attendeeModel.save().done(function() {
                        that.toggleEditHandler();
                    });
                });

            } else {
                this.attendeeModel.save().done(function() {
                    that.toggleEditHandler();
                });
            }
        }
    }

});

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