(function () {
    'use strict';

    angular
        .module('app.controllers')
        .controller('DogCtrl', ['$rootScope', '$location','$interval', '$document','$scope', 'dog', 'DogService', 'MapService', DogCtrl]);

    function DogCtrl($rootScope, $location ,$interval, $document, $scope, dog, DogService, MapService) {
        console.log('Controller: DogCtrl');

        if(!dog) {
            console.log('dog is null');
            return;
        }

        var refresh,
            map,
            status,
            current_dog_id,
            close_dogs = new Array();

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
        }

        function init() {
            map = new ymaps.Map(document.getElementById("map"), {
                center: [57.789939, 47.879478],
                zoom: 17
            });
        }

        $scope.fight = function() {
            if ( angular.isDefined(refresh) ) return;
            refresh = $interval(function() {
                DogService.getLastEvents(dog.id, event).then(function success(response){
                    status = response.data;
                    event = status.event_counter;
                    if(status.walk != null){
                        if(status.walk.length != 0){
                            setCenter(status.walk[status.walk.length - 1]);
                        }
                        if (status.close_dogs_events) {
                            for (var count = 0; count < status.close_dogs_events.length; count++) {
                                if (arrayObjectIndexOf(close_dogs, status.close_dogs_events[count])  == -1) {
                                    if(status.close_dogs_events[count].became_close)
                                    {
                                        if(status.close_dogs_events[count].status == 1)
                                        {
                                            alert("Friend: " + status.close_dogs_events[count].dog.nick);
                                        }
                                        else
                                        {
                                            alert("Enemy: " + status.close_dogs_events[count].dog.nick);
                                        }
                                    }
                                    close_dogs.push(status.close_dogs_events[count]);
                                    ctrl.hidden = true;
                                    $rootScope["close_dogs"] = close_dogs;
                                }
                            }
                        }
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

        function arrayObjectIndexOf(myArray, searchTerm) {
            for(var i = 0, len = myArray.length; i < len; i++) {
                if (myArray[i].dog.id == searchTerm.dog.id) {
                    myArray[i] = searchTerm;
                    return 0;
                }
            }
            return -1;
        }

        function setCenter(coords){
            MapService.setCenter(map, coords);
        }

        return ctrl;
    }
})();