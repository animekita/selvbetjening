
/** Events **/

var SubOption = Backbone.RelationalModel.extend({
    urlRoot: '/api/rest/v1/suboption/'
});

var SubOptions = Backbone.Collection.extend({
    urlRoot: '/api/rest/v1/suboption/',
    model: SubOption
});

var Option = Backbone.RelationalModel.extend({
    urlRoot: '/api/rest/v1/option/',

    relations: [
        {
            type: Backbone.HasMany,
            key: 'suboptions',
            relatedModel: 'SubOption',
            collectionType: 'SubOptions'
        }
    ]
});

var Options = Backbone.Collection.extend({
    urlRoot: '/api/rest/v1/option/',
    model: Option
});

var OptionGroup = Backbone.RelationalModel.extend({
    urlRoot: '/api/rest/v1/optiongroup/',

    relations: [
        {
            type: Backbone.HasMany,
            key: 'options',
            relatedModel: 'Option',
            collectionType: 'Options'
        }
    ]
});

var OptionGroups = Backbone.Collection.extend({
    urlRoot: '/api/rest/v1/optiongroup/',
    model: OptionGroup
});

var Event = Backbone.RelationalModel.extend({
    urlRoot: '/api/rest/v1/event/',

    relations: [
        {
            type: Backbone.HasMany,
            key: 'option_groups',
            relatedModel: 'OptionGroup',
            collectionType: 'OptionGroups'
        }
    ]
});

var Events = Backbone.Collection.extend({
    urlRoot: '/api/rest/v1/event/',
    model: Event
});