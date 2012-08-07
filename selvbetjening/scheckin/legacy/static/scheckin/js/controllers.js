
angular.module('scheckin', ['ngResource', 'scheckin-services']).
    config(function($provide, $routeProvider) {

    $routeProvider.
        when('/:eventId/attendees', {
            templateUrl: '/static/scheckin/partials/attendees.html',
            controller: AttendeeListController
        }).
        when('/:eventId/attendees/:attendeeId', {
            templateUrl: '/static/scheckin/partials/attendee.html',
            controller: AttendeeController
        }).
        when('/', {
            templateUrl: '/static/scheckin/partials/selectevent.html',
            controller: EventSelectionController
        }).
        otherwise({
            redirectTo: '/'
        });
});

function AttendeeListController($scope, $routeParams, eventService) {

    $scope.event = eventService.get($routeParams.eventId);
    $scope.event.loadAttendees();

}

function AttendeeController($scope, $http, $resource, $routeParams, eventService) {

    $scope.event = eventService.get($routeParams.eventId);

    $scope.selections = {};
    var selections_original = {};

    $scope.attendee = $resource('/api/rest/v1/attendee/:attendeeId/?format=json',
        {
            attendeeId: $routeParams.attendeeId
        },
        {
            save: {method: 'PUT'},
            create: {method: 'POST'}
        }).get(function() {
            for (var i = 0; i < $scope.attendee.selections.length; i++) {
                var selection = $scope.attendee.selections[i];
                $scope.selections[selection['option']] = true;
                selections_original[selection['option']] = true;
            }
        });

    $scope.saveSelections = function() {

        var patch = {
            'objects': [],
            'deleted_objects': []
        };

        // remove unchecked elements
        for (var i = 0; i < $scope.attendee.selections.length; i++) {
            var selection = $scope.attendee.selections[i];

            if ($scope.selections[selection['option']] == false) {
                patch["deleted_objects"].push(selection['resource_uri']);
            }
        }

        // add new elements
        for (var optionUri in $scope.selections) {
            if ($scope.selections[optionUri] == true &&
                selections_original[optionUri] == undefined) {

                patch["objects"].push({
                    "attendee": $scope.attendee.resource_uri,
                    "option": optionUri,
                    "suboption": null
                });
            }
        }

        $http.defaults.headers.patch = {"Content-Type": "application/json"};

        var request = {
            method: "patch",
            url: "http://localhost:8000/api/rest/v1/selection/?format=json",
            data: patch
        };

        $http(request).
            success(function(data, status, headers, config) {

            });

        //$scope.attendee.$save();
    }
}

function EventSelectionController($scope, eventService) {

    $scope.events = eventService.events;
    $scope.eventListLimit = 5;

}
