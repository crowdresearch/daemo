/**
 * Requester
 * @namespace crowdsource.requester.services
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.requester.services')
        .factory('Requester', Requester);

    Requester.$inject = ['$cookies', '$http', '$q'];

    /**
     * @namespace Requester
     * @returns {Factory}
     */

    function Requester($cookies, $http, $q) {
        /**
         * @name Requester
         * @desc The Factory to be returned
         */
        var Requester = {
            getRequesterPrivateProfile: getRequesterPrivateProfile,
            getRequesterTaskPortfolio: getRequesterTaskPortfolio

        };

        return Requester;

        function getRequesterPrivateProfile(profileid) {
            var settings = {
                url: '/api/requester/' + profileid + '/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function getRequesterTaskPortfolio() {
            var settings = {
                url: 'api/requester/1/portfolio/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }


    }
})();
