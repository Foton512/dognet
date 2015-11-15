(function () {
    'use strict';

    angular
        .module('app.controllers')
        .controller('RelationsCtrl', ['$window', '$rootScope', 'dog', '$scope', '$document', '$interval', 'DogService', RelationsCtrl]);

    function RelationsCtrl($window, $rootScope, dog, $scope, $document, $interval, DogService) {
        console.log('Controller: RelationsCtrl');

        if(!dog) {
            console.log('dog is null');
            return;
        }
        var event = 0;
        var status;
        var refresh;
        var close_dogs = new Array();

        $document.ready(function () {
            ctrl.hidden = true;
            ctrl.relations = $rootScope['close_dogs'];
            ctrl.dog = dog;
            console.log(ctrl.relations[0].dog_id);
            $scope.fight();
        });

        function setRelation(dogId, relationDogId, statusValue){
            DogService.changeRelation(dogId, relationDogId, statusValue);
        }

        function setVisible(statusValue, statusButton){
            if(statusButton == statusValue){
                return false
            }
            else if(statusButton == -statusValue){
                return true;
            }
            else
            {
                return true;
            }
        }

        function getDogById(id)
        {
            return DogService.getById(id);
        }

        $scope.fight = function() {
            if (angular.isDefined(refresh)) return;
            refresh = $interval(function () {
                DogService.getLastEvents(dog.id, event).then(function success(response) {
                    status = response.data;
                    event = status.event_counter;
                    if(status.walk != null){
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
                                    ctrl.relations = $rootScope['close_dogs'];
                                }
                            }
                        };
                    }
                }, 2000);
            })
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

        function arrayObjectIndexOf(myArray, searchTerm) {
            for(var i = 0, len = myArray.length; i < len; i++) {
                if (myArray[i].dog.id == searchTerm.dog.id) {
                    myArray[i] = searchTerm;
                    return 0;
                }
            }
            return -1;
        }

        function getAddress()
        {
            return $window.localStorage.getItem('serverAddress');
        }

        var ctrl = this;

        ctrl = {
            setRelation : setRelation,
            setVisible : setVisible,
            getDogById : getDogById,
            getAddress : getAddress
        };

        return ctrl;
    }
})();