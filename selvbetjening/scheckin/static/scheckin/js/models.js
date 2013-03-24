
/** Attendees **/

var Comment = Backbone.Model.extend({
    urlRoot: '/api/rest/v1/attendeecomment/'
});

var Comments = Backbone.Collection.extend({
    urlRoot: '/api/rest/v1/attendeecomment/',
    model: Comment
});

var Payment = Backbone.Model.extend({
    urlRoot: '/api/rest/v1/payment/'
});

var Payments = Backbone.Collection.extend({
    urlRoot: '/api/rest/v1/payment/',
    model: Payment
});

var Selection = Backbone.Model.extend({
    urlRoot: '/api/rest/v1/selection/'
});

var Selections = Backbone.Collection.extend({
    urlRoot: '/api/rest/v1/selection/',
    model: Selection
});

var Attendee = Backbone.Model.extend({
    urlRoot: '/api/rest/v1/attendee/',

    mutators: {
        isWaiting: function() {
            return this.state == 'waiting';
        },
        isAccepted: function() {
            return this.state == 'accepted';
        },
        isCheckedin: function() {
            return this.state == 'attended';
        },
        hasPaid: function() {
            return this.invoice ? this.invoice.amount_paid >= this.invoice.amount_total : false;
        },
        hasPaymentDue: function() {
            return this.invoice ? this.invoice.amount_paid < this.invoice.amount_total : false;
        },
        paymentDue: function() {
            return this.invoice ? this.invoice.amount_total - this.invoice.amount_paid : 0;
        },
        hasCashbackDue: function() {
            return this.invoice ? this.invoice.amount_paid > this.invoice.amount_total : false;
        }
    },

    parse: function(response) {
        if (response) {
            response.invoice.amount_paid = parseInt(response.invoice.amount_paid);
            response.invoice.amount_total = parseInt(response.invoice.amount_total);
            response.invoice.invoiceId = parseInt(response.invoice.resource_uri.split("/")[5]);
            response.attendeeId = parseInt(response.resource_uri.split("/")[2]);
        }
        return response;
    }
});

var Attendees = Backbone.Collection.extend({
    urlRoot: '/api/rest/v1/attendee/',
    model: Attendee
});

/** Events **/

var SubOption = Backbone.Model.extend({
    urlRoot: '/api/rest/v1/suboption/'
});

var SubOptions = Backbone.Collection.extend({
    urlRoot: '/api/rest/v1/suboption/',
    model: SubOption
});

var Option = Backbone.Model.extend({
    urlRoot: '/api/rest/v1/option/'
});

var Options = Backbone.Collection.extend({
    urlRoot: '/api/rest/v1/option/',
    model: Option
});

var OptionGroup = Backbone.Model.extend({
    urlRoot: '/api/rest/v1/optiongroup/'
});

var OptionGroups = Backbone.Collection.extend({
    urlRoot: '/api/rest/v1/optiongroup/',
    model: OptionGroup
});

var Event = Backbone.Model.extend({
    urlRoot: '/api/rest/v1/event/'
});

var Events = Backbone.Collection.extend({
    urlRoot: '/api/rest/v1/event/',
    model: Event
});
