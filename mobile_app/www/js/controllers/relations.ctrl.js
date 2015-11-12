(function () {
    'use strict';

    angular
        .module('app.controllers')
        .controller('RelationsCtrl', ['dog', '$document', '$scope', '$interval', 'DogService', RelationsCtrl]);

    function RelationsCtrl(dog, $document, $scope, $interval, DogService) {
        console.log('Controller: RelationsCtrl');

        if(!dog) {
            console.log('dog is null');
            return;
        }
        var event = 0;
        var status;
        var refresh;
        $document.ready(function () {
            ctrl.hidden = false;
            if(!window.localStorage.getItem('access_token')){
                $state.go('app.auth');
            }else{
                $scope.fight();
            }
        });

        $scope.fight = function() {
            if ( angular.isDefined(refresh) ) return;
            refresh = $interval(function() {
                DogService.getLastEvents(dog.id, event).then(function success(response){
                    status = response.data;
                    event = status.event_counter;
                    if(status.close_dogs_events){
                        console.log(status.close_dogs_events.length);
                        ctrl.relations = status.close_dogs_events;
                        ctrl.hidden = true;
                    }else{
                        ctrl.hidden = false;
                    }
                });

            }, 1000);
        };

        $scope.$on('$locationChangeStart', function() {
            $scope.stopRefresh();
        });

        $scope.stopRefresh = function() {
            if (angular.isDefined(refresh)) {
                $interval.cancel(refresh);
                refresh = undefined;
            }
        };

        var ctrl = this;

        return ctrl;
    }
})();