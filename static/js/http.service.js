/**
 * Http service master.
 * @namespace crowdsource.services
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.services', [])
        .factory('HttpService', HttpService);

    HttpService.$inject = ['$cookies', '$http', '$q', '$location', '$window'];


    function HttpService($cookies, $http, $q, $location, $window) {
        /**
         * @name HttpService
         * @desc The Factory to be returned
         */
        var HttpService = {
            doRequest: doRequest,
            apiPrefix: '/api'
        };

        return HttpService;


        function doRequest(settings) {

            var deferred = $q.defer();

            $http(settings).success(function (data, status, headers, config) {
                deferred.resolve(arguments);
            }).error(function (data, status, headers, config) {
                deferred.reject(arguments);

            });
            return deferred.promise;
        }
    }
})();
