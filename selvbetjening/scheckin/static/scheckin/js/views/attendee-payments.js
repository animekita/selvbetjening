
var AttendeePaymentsView = Backbone.Layout.extend({
    template: "#attendee-payments-template",

    attendeeModel: null,
    paymentsCollection: null,

    inHiddenState: true,
    isLoading: false,

    initialize: function(options) {
        this.attendeeModel = options.attendeeModel;
    },

    beforeRender: function() {
        if (this.paymentsCollection === null && this.attendeeModel.get('invoice') !== undefined) {

            this.isLoading = true;

            this.paymentsCollection = new Payments();
            this.paymentsCollection.on('reset', function() {
                this.isLoading = false;
                this.render();
            }, this);
            this.paymentsCollection.fetch({
                data: {
                    limit: 0,
                    invoice: this.attendeeModel.get('invoice').invoiceId
                },
                reset: true
            });
        }
    },

    serialize: function() {
        return {
            hidden: this.inHiddenState,
            loading: this.isLoading,
            paymentsCollection: this.paymentsCollection === null ? null : this.paymentsCollection.toJSON()
        };
    },

    reset: function() {
        this.isLoading = false;
        this.paymentsCollection = null;

        this.render();
    },

    show: function() {
        this.inHiddenState = false;
        this.render();
    },

    hide: function() {
        this.inHiddenState = true;
        this.render();
    },

    isHidden: function() {
        return this.inHiddenState;
    }

});