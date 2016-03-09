/**
 * User
 * @namespace crowdsource.user.services
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.user.services')
        .factory('User', User);

    User.$inject = ['$cookies', '$http', '$q', 'HttpService'];

    /**
     * @namespace User
     * @returns {Factory}
     */

    function User($cookies, $http, $q, HttpService) {
        var User = {
            getProfile: getProfile,
            listUsernames: listUsernames,
            setOnline: setOnline,
            setOffline: setOffline
        };
        return User;

        function getProfile(username) {
            var settings = {
                url: '/api/profile/' + username + '/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function listUsernames(pattern) {
            var settings = {
                url: '/api/user/list-username/?pattern=' + pattern,
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function setOnline() {
            var settings = {
                url: '/api/user/online/',
                method: 'POST'
            };
            return HttpService.doRequest(settings);
        }

        function setOffline() {
            var settings = {
                url: '/api/user/offline/',
                method: 'POST'
            };
            return HttpService.doRequest(settings);
        }
    }

})();
