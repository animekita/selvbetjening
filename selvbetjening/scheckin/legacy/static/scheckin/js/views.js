
var EventListItemView = Backbone.View.extend({
    template: "#event-list-item-template",
    tagName: "tr"
});

var EventListView = Backbone.View.extend({
    template: "#event-list-template",

    initialize: function() {
        this.collection.on("change", function() {
            this.render();
        }, this);
    },

    render: function(manage) {
        this.collection.each(function(model) {
            this.insertView(new EventListItemView({
                model: model
            }));
        }, this);

        return manage(this).render();
    }
});


$(function() {

    Backbone.LayoutManager.configure({
        fetch: function (path){
            return Handlebars.compile($(path).html());
        },
        render: function(template, context) {
            return template(context);
        }
    });


    var events = new Events();
    events.fetch();

    var main = new Backbone.LayoutManager({
        template: "#chrome-layout",

        views: {
            "#main-view": new EventListView({
                collection: events
            })
        }
    });

    $("body").html(main.el);
    main.render();

    window.a = events;
});


