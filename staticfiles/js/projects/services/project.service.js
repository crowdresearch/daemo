/**
 * Project Service
 * Author: Shirish Goyal
 */
(function () {
    'use strict';
    angular.module('crowdsource.projects.services', ['crowdsource'])
        .service('ProjectService', ProjectService);

    ProjectService.$inject = ['$http', '$log', '$q', 'CONSTANTS'];

    /**
     *
     * @param $http
     * @param $log
     * @param CONSTANTS
     * @returns {{list: list}}
     * @constructor
     */
    function ProjectService($http, $log, $q, CONSTANTS) {

        return {
            list: list
        };

        /**
         *
         * @param chunk
         * @param page
         * @returns {*}
         */
        function list(chunk, page) {
            var d = $q.defer();

            $http.get(CONSTANTS.API_URL + '/projects/', {
                params: {
                    chunk: chunk,
                    offset: (page - 1) * chunk
                }
            })
                .success(function (response, status, headers) {
                    d.resolve(response);
                })
                .error(function (response, status, headers, config, errors) {
                    d.reject(response);
                });

            return d.promise;
        }
    }

})();
