(function () {
    'use strict';

    angular
        .module('app.controllers', [])
        .controller('MainCtrl', ['$rootScope', '$window', MainCtrl]);

    function MainCtrl($rootScope, $window) {
        console.log('Controller: MainCtrl');
        $rootScope.$on("$stateChangeStart", function () {
            $rootScope.loading = true;
            $window.localStorage.setItem('serverAddress', 'http://188.166.64.150:8000/');
        });
        $rootScope.$on("$viewContentLoaded", function () {
            $rootScope.loading = false;
        });
        $rootScope.back = function () {
            $window.history.back();
        };
    }
})();