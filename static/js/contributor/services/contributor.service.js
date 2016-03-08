/**
 * Contributor
 * @namespace crowdsource.contributor.services
 * @author shirish
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.contributor.services')
        .factory('Contributor', Contributor);

    Contributor.$inject = ['$cookies', '$http', '$q', 'HttpService', 'LocalStorage'];

    /**
     * @namespace Contributor
     * @returns {Factory}
     */

    function Contributor($cookies, $http, $q, HttpService, LocalStorage) {
        /**
         * @name Contributor
         * @desc The Factory to be returned
         */

        var Contributor = {
            getAll: getAll
        };

        return Contributor;

        function getAll(){
            return $http.get('/static/js/contributor/data/contributors.json');
        }
    }
})();
