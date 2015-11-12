(function () {
    'use strict';

    angular
        .module('app.controllers')
        .controller('AuthCtrl', ['$state', '$http','VkLoginService', AuthCtrl]);

    function AuthCtrl($state, $http, VkLoginService) {
        var ctrl = this;
        ctrl = {
            auth : authorization
        };

        return ctrl;

        function authorization() {
            VkLoginService.auth().then(getAccessTokenFromServer);
        }

        function getAccessTokenFromServer() {
            $http({
                method: 'GET',
                url: 'http://188.166.64.150:8000/auth/vk-oauth2/?access_token='
                + window.localStorage.getItem("plugin_vk_token")
            }).then(function successCallback(response) {
                window.localStorage.setItem('access_token', response.data["access_token"]);
                $state.go('app.home');
            });
        }
	}
})();