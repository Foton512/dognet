(function () {
    'use strict';

    angular
        .module('app.services')
        .factory('DogService', ['RequestService', DogService]);

    function DogService(RequestService) {
        var svc = this;
        svc = {
            getById : getById,
            getLastEvents: getLastEvents,
            changeRelation : changeRelation
        };

        function getById(id){
            return RequestService.getById(id).then(function successCallback(response) {
                return response.data;
            });
        }

        function getLastEvents(dogId, eventCount){
            return RequestService.getLastEvents(dogId, eventCount);
        }

        function changeRelation(dogId, relatedDogId, statusValue)
        {
            return RequestService.setRelation(dogId, relatedDogId, statusValue)
                .then(function successCallback(response)
                {
                });
        }

        return svc;
    }
})();