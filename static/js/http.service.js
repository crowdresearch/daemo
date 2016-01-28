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

    /**
     * @namespace HttpService
     * @returns {Factory}
     */

    function HttpService($cookies, $http, $q, $location, $window) {
        /**
         * @name HttpService
         * @desc The Factory to be returned
         */
        var HttpService = {
            doRequest: doRequest
        };

        return HttpService;


        /**
         * @name doRequest
         * @desc Performs a given request.
         * @returns {Promise}
         * @memberOf crowdsource.tasksearch.services.HttpService
         */
        function doRequest(settings) {

            var deferred = $q.defer();
            //Authentication.attachHeaderTokens(settings); // until we write OAUTH2 encryption middleware

            $http(settings).success(function (data, status, headers, config) {
                deferred.resolve(arguments);
            }).error(function (data, status, headers, config) {
                deferred.reject(arguments);

            });
            return deferred.promise;
        }
    }
})();
