(function () {
    'use strict';

    angular
        .module('app.controllers')
        .controller('DogCtrl', ['$location','$interval', '$document','$scope', 'dog', 'DogService', 'MapService', DogCtrl]);

    function DogCtrl($location ,$interval, $document, $scope, dog, DogService, MapService) {
        console.log('Controller: DogCtrl');

        if(!dog) {
            console.log('dog is null');
            return;
        }

        var refresh,
            map,
            status,
            current_dog_id;
        var ctrl = this;
        var event = 0;
        ctrl = {
            dog : dog,
            setCenter: setCenter
        };

        $document.ready(function () {
            initializeMap();
            ctrl.hidden = false;
        });

        function initializeMap() {
            ymaps.ready(init);
            $scope.fight();
        };

        function init() {
            map = new ymaps.Map(document.getElementById("map"), {
                center: [57.789939, 47.879478],
                zoom: 17
            });
        };

        $scope.fight = function() {
            if ( angular.isDefined(refresh) ) return;
            refresh = $interval(function() {
                DogService.getLastEvents(dog.id, event).then(function success(response){
                    status = response.data;
                    event = status.event_counter;
                    if(status.walk.path.length != 0){
                        setCenter([status.walk.path[0].lat, status.walk.path[0].lon])
                    }
                    if(status.close_dogs_events.lenght != 0 && status.close_dogs_events.lenght){
                        ctrl.hidden = true;
                    }else{
                        ctrl.hidden = false;
                    }
                });

            }, 1000);
        };

        $scope.$on('$locationChangeStart', function() {
            map.destroy();
            $scope.stopRefresh();
        });

        $scope.stopRefresh = function() {
            if (angular.isDefined(refresh)) {
                $interval.cancel(refresh);
                refresh = undefined;
            }
        };

        function setCenter(coords){
            MapService.setCenter(map, coords);
        }

        return ctrl;
    }
})();