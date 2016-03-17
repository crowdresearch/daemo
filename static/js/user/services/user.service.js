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
            updateProfile: updateProfile,
            getCountries: getCountries,
            getCities: getCities,
            getJobTitles: getJobTitles,
            updatePreferences: updatePreferences
        };

        return User;

        function getProfile(username) {
            var settings = {
                url: '/api/profile/' + username + '/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function updateProfile(username, data) {
            var settings = {
                url: '/api/profile/' + username + '/',
                method: 'PUT',
                data: JSON.stringify(data)
            };
            return HttpService.doRequest(settings);
        }

        function getCountries() {
            var settings = {
                url: "/api/country/",
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function getCities() {
            var settings = {
                url: "/api/city/",
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function getJobTitles() {
            return $http.get('/static/js/user/data/job_titles.json');
        }

        function updatePreferences(username, data) {
            var settings = {
                url: '/api/preferences/' + username + '/',
                method: 'PUT',
                data: data
            };
            return HttpService.doRequest(settings);
        }
    }

})();