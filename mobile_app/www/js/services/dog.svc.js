(function () {
    'use strict';

    angular
        .module('app.services')
        .factory('DogService', ['RequestService', DogService]);

    function DogService(RequestService) {
        var svc = this;
        svc = {
            getById : getById,
            getLastEvents: getLastEvents
        };

        function getById(id){
            return RequestService.getById(id).then(function successCallback(response) {
                return response.data;
            });
        }

        function getLastEvents(dogId, eventCount){
            return RequestService.getLastEvents(dogId, eventCount);
        }

        return svc;
    }
})();