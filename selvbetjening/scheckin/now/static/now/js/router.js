
var Router = Backbone.Router.extend({

    routes: {
        "": "attendees",
        "attendee/:attendeeId/" : "attendee"
    }

});
