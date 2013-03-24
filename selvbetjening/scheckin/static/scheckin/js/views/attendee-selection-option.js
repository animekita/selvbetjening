
var AttendeeSelectionOptionView = Backbone.Layout.extend({
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

        var checked = this.$('input:checkbox')[0].checked;

        console.log("modelCHecked: " + this.modelChecked + " checked: " + checked);
        if (checked != this.modelChecked) {

            if (checked) {
                // add it
                console.log('commit');
                this.selectionModel.save();
                this.modelChecked = true;

            } else {
                // delete it
                console.log('rewoke');
                this.selectionModel.destroy({
                    success: function(model) {
                        model.unset('id');
                        model.unset('resource_uri');
                    }
                });

                this.modelChecked = false;
            }

        } else {
            console.log('hunh');
        }
    },

    afterRender: function() {
        this.$('input:checkbox').attr('checked', this.modelChecked);
    }
});