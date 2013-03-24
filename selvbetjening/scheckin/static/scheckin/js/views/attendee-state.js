
var AttendeeStateView = Backbone.Layout.extend({
    template: "#attendee-state-template",

    attendeeModel: null,
    eventModel: null,

    paymentsView: null,

    events: {
        'click .doCheckIn': 'checkInHandler',
        'click .doCheckOut': 'checkOutHandler',

        'click .doShowPayments': 'showPayments',
        'click .doHidePayments': 'hidePayments',

        'click .doPay': 'payHandler',
        'submit .doCustomPay': 'customPayHandler'
    },

    initialize: function(options) {
        this.attendeeModel = options.attendeeModel;
        this.attendeeModel.on('change', this.render, this);

        this.eventModel = options.eventModel;

        this.paymentsView = new AttendeePaymentsView({
            attendeeModel: options.attendeeModel
        });
    },

    beforeRender: function() {
        this.setView('.attendeePayments', this.paymentsView).render();
    },

    serialize: function() {
        return {
            attendee: this.attendeeModel.toJSON(),
            paymentsHidden: this.paymentsView.isHidden()
        };
    },

    _enterSavingMode: function() {
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

    showPayments: function() {
        this.paymentsView.show();
        this.render();
    },

    hidePayments: function() {
        this.paymentsView.hide();
        this.render();
    },

    checkInHandler: function() {

        this._enterSavingMode();

        this.attendeeModel.set('state', 'attended');

        var that = this;
        this.attendeeModel.save().done(function() {
            that.attendeeModel.fetch().done(function() {
                that.render();
            });
        });
    },

    checkOutHandler: function() {

        this._enterSavingMode();

        this.attendeeModel.set('state', 'accepted');

        var that = this;
        this.attendeeModel.save().done(function() {
            that.attendeeModel.fetch().done(function() {
                that.render();
            });
        });

    },

    payHandler: function() {

        this._enterSavingMode();

        var payment = new Payment({
            amount: this.attendeeModel.get('paymentDue'),
            note: "Automatic payment through nem check-in",
            invoice: this.attendeeModel.get('invoice').resource_uri
        });

        var that = this;
        payment.save().done(function() {
            that.attendeeModel.fetch().done(function() {
                that.paymentsView.reset();
                that.render();
            });
        });
    },

    customPayHandler: function(e) {

        e.stopPropagation();
        e.preventDefault();

        this._enterSavingMode();

        //this.attendeeModel.set('state', this.$('form[name=attendeeForm] input:radio[name=state]:checked').val());

        var paymentAmount = this.$('form[name=attendeePaymentForm] input[name=paymentAmount]').val();

        if (paymentAmount == undefined) {
            return;
        }

        paymentAmount = parseFloat(paymentAmount.replace(',', '.'));

        if (paymentAmount == 0 || isNaN(paymentAmount)) {
            this.render();
            return;
        }

        var payment = new Payment({
            amount: paymentAmount,
            note: "Automatic payment through nem check-in",
            invoice: this.attendeeModel.get('invoice').resource_uri
        });

        var that = this;
        payment.save().done(function() {
            that.attendeeModel.save().done(function() {
                that.attendeeModel.get('invoice').total_paid += paymentAmount;
                that.paymentsView.reset();
                that.render();
            });
        });
    }

});