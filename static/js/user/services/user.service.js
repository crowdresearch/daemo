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
            updateProfile: updateProfile,
            getCountries: getCountries,
            getCities: getCities
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
                url: '/api/profile/' + username + '/update_profile/',
                method: 'POST',
                data: JSON.stringify(data)
            };
            return HttpService.doRequest(settings);
        }

        function getCountries() {
            var countries = [];
            $http({
                method: "GET",
                url: "/api/country/"
            }).then(function success(response) {
                response.data.forEach(function (data) {
                    countries.push(data);
                })
            });
            return countries;
        }

        function getCities(){
            var cities = [];
            $http({
                method: "GET",
                url: "/api/city/"
            }).then(function success(response) {
                response.data.forEach(function (data) {
                    cities.push(data);
                })
            });
            return cities;
        }
    }

})();