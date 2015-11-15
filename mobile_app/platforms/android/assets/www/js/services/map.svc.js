(function () {
    'use strict';

    angular
        .module('app.services')
        .factory('MapService',  MapService);

    function MapService() {
        var svc = this;
        svc = {
            setCenter : setCenter
        };

        function setCenter(map, coords)
        {
            map.setCenter(coords);
        }

        return svc;
    }
})();