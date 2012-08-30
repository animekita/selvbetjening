
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