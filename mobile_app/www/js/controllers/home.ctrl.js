(function () {
    'use strict';

    angular
        .module('app.controllers')
        .controller('HomeCtrl', ['$scope', '$interval', '$state', '$document', 'RequestService', HomeCtrl]);

    function HomeCtrl($scope, $interval, $state, $document, RequestService) {
        var ctrl = this;
        var tmp,
            refresh;

        ctrl = {
        };

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
                console.log(1111);
                RequestService.getMyDogs().then(function successCallback(response) {
                    tmp = response.data;
                    if(tmp == ""){
                        ctrl.hidden = true;
                        console.log(ctrl.hidden);
                    }else{
                        ctrl.dogs = tmp;
                        ctrl.hidden = false;
                    }
                });
            }, 1000);
        };

        $scope.$on('$destroy', function() {
            $scope.stopRefresh();
        });

        $scope.stopRefresh = function() {
            if (angular.isDefined(refresh)) {
                $interval.cancel(refresh);
                refresh = undefined;
            }
        };

        return ctrl;
    }
})();