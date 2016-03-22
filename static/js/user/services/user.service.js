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
            updatePreferences: updatePreferences,
            setOnline: setOnline,
            create_or_update_aws: create_or_update_aws,
            get_aws_account: get_aws_account,
            removeAWSAccount: removeAWSAccount
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

        function updatePreferences(username, data) {
            var settings = {
                url: '/api/preferences/' + username + '/',
                method: 'PUT',
                data: data
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

        function create_or_update_aws(data) {
            var settings = {
                url: '/api/mturk-account',
                method: 'POST',
                data: data
            };
            return HttpService.doRequest(settings);
        }

        function get_aws_account() {
            var settings = {
                url: '/api/mturk-account',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }
        function removeAWSAccount() {
            var settings = {
                url: '/api/mturk-account/remove',
                method: 'DELETE'
            };
            return HttpService.doRequest(settings);
        }
    }

})();
