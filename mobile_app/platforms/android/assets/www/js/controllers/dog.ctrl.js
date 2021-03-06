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
            home,
            myDog,
            close_dogs = new Array(),
            way;
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
                center: [57.689631, 39.778299],
                zoom: 17
            });
            home = new ymaps.Placemark([57.689631, 39.778299],
            {
                hintContent: dog.nick
            }
            );

            map.geoObjects.add(home);
            map.controls.remove('searchControl');
            map.controls.remove('trafficControl');
            map.controls.remove('geolocationControl');
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


                            map.geoObjects.remove(myDog);
                            map.geoObjects.remove(way);

                            myDog  = new ymaps.Placemark(status.walk[status.walk.length - 1]);
                            way = new ymaps.Polyline(
                                status.walk
                            );
                            map.geoObjects.add(myDog);
                            map.geoObjects.add(way);
                        }
                        if (status.close_dogs_events) {
                            for (var count = 0; count < status.close_dogs_events.length; count++) {
                                if (arrayObjectIndexOf(close_dogs, status.close_dogs_events[count])  == -1) {
                                    close_dogs.push(status.close_dogs_events[count]);
                                    if(status.close_dogs_events[count].became_close == true)
                                    {
                                        if(status.close_dogs_events[count].status == 1)
                                        {
                                            alert("Friend: " + status.close_dogs_events[count].dog.nick);
                                        }
                                        else if(status.close_dogs_events[count].status == -1)
                                        {
                                            alert("Enemy: " + status.close_dogs_events[count].dog.nick);
                                        }
                                    }
                                    ctrl.hidden = true;
                                    $rootScope["close_dogs"] = close_dogs;
                                }
                            }
                        }
                    }
                });
            }, 2000);
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
                alert(11111);
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