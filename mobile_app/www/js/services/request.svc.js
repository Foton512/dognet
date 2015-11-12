(function () {
    'use strict';

    angular
        .module('app.services')
        .factory('RequestService', ['$http', '$window', RequestService]);

    function RequestService($http, $window) {
        var svc = this;
        svc = {
            getMyDogs : getMyDogs,
            getById : getById,
            getLastEvents : getLastEvents
        }

        function getMyDogs(){
            return $http({
                method: 'GET',
                url: $window.localStorage.getItem('serverAddress') + 'api/dog/get_list/',
                headers: {
                    'Authorization': window.localStorage.getItem('access_token')
                }
            })
        }

        function getById(id){
            return $http({
                method: 'GET',
                url: $window.localStorage.getItem('serverAddress') + 'api/dog/get/?id=' + id,
                headers: {
                    'Authorization': window.localStorage.getItem('access_token')
                }
            })
        }

        function getLastEvents(dogId, eventsCount){
            return $http({
                method: 'GET',
                url: $window.localStorage.getItem('serverAddress') + 'api/dog/get_events?id=' + dogId + '&fields=lat,lon,close_dogs_events,walk&event_counter=' + eventsCount,
                headers: {
                    'Authorization': window.localStorage.getItem('access_token')
                }
            })
        }

        return svc;
    }
})();