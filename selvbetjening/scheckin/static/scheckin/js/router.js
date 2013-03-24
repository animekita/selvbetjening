
var Router = Backbone.Router.extend({

    routes: {
        "attendee/:attendeeId/" : "attendee",
        "": "attendees"
    },

    gotoAttendee: function(attendeeId) {
        this.navigate("attendee/" + attendeeId + "/", {trigger: true});
    }

});
