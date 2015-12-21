/**
 * User
 * @namespace crowdsource.user.services
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.user.services')
        .factory('User', User);

    User.$inject = ['$cookies', '$http', '$q', '$location', 'HttpService'];

    /**
     * @namespace User
     * @returns {Factory}
     */

    function User($cookies, $http, $q, $location, HttpService) {
        var User = {
            getProfile: getProfile,
            updatePreferences: updatePreferences,
            getPreferences: getPreferences

        };
        return User;

        function getProfile(username) {
            var settings = {
                url: '/api/profile/' + username + '/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function updatePreferences(preferences, username){
            var settings = {
                url: '/api/preferences/' + username + '/',
                method: 'PUT',
                data: preferences
            };
            return HttpService.doRequest(settings);
        }
        function getPreferences(username){
            var settings = {
                url: '/api/preferences/' + username + '/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }
    }

})();