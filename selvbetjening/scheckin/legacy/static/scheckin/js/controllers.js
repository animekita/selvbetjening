
angular.module('scheckin-services', ['ngResource']).
    config(function($provide) {

    $provide.factory('attendeeService', function($http) {

        var attendeeService = {

            attendees : [],
            attendeesLoaded : false,
            attendeesLoadProgress : 0,

            loadAttendeesPartial: function(event, offset) {

                var url = '/api/rest/v1/attendee/?event=' + event + '&offset=' + offset + '&format=json';

                var that = this;

                $http.get(url).success(function(data) {
                    that.attendees = that.attendees.concat(data.objects);

                    var loaded = parseInt(data.meta.offset) + parseInt(data.meta.limit);
                    var total = parseInt(data.meta.total_count);
                    var last = loaded >= total;

                    if (last) {
                        that.attendeesLoaded = true;
                    } else {
                        that.attendeesLoadProgress = parseInt((loaded / total) * 100);
                        that.loadAttendeesPartial(event, loaded);
                    }
                });
            }

        };

        attendeeService.loadAttendeesPartial(41, 0);

        return attendeeService;

    });

    $provide.factory('eventService', function($resource) {

        return $resource('/api/rest/v1/event/?format=json').get()

    });

    });

angular.module('scheckin', ['ngResource', 'scheckin-services']).
    config(function($provide, $routeProvider) {

    $routeProvider.
        when('/attendees', {
            templateUrl: '/static/scheckin/partials/attendees.html',
            controller: AttendeeListController
        }).
        when('/attendees/:attendeeId', {
            templateUrl: '/static/scheckin/partials/attendee.html',
            controller: AttendeeController
        }).
        otherwise({
            redirectTo: '/attendees'
        });
});

function AttendeeListController($scope, attendeeService) {

    $scope.attendeeService = attendeeService;

}

function AttendeeController($scope, $resource, $routeParams) {

    $scope.attendee = $resource('/api/rest/v1/attendee/:attendeeId/?format=json', {
        attendeeId: $routeParams.attendeeId
    }, {
        save: {method: 'PUT'},
        create: {method: 'POST'}
    }).get();

    $scope.checkin = function() {
        $scope.attendee.$save();
    }
}

function EventSelectorController($scope, eventService) {
    $scope.eventService = eventService;
}

$(function() {
    $('.dropdown-toggle').dropdown();
});