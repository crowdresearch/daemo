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

    Contributor.$inject = ['$cookies', '$http', '$q', '$location', 'HttpService', 'LocalStorage'];

    /**
     * @namespace Contributor
     * @returns {Factory}
     */

    function Contributor($cookies, $http, $q, $location, HttpService, LocalStorage) {
        /**
         * @name Contributor
         * @desc The Factory to be returned
         */

        var Contributor = {
            getAll: getAll,
            getHighlighted: getHighlighted
        };

        return Contributor;

        function getAll(){
            var contributors = [
                {
                    name:'Michael Bernstein',
                    country:'USA'
                },
                {
                    name:'Rajan Vaish',
                    country:'USA'
                },
                {
                    name: 'Neil',
                    country: 'USA'
                },
                {
                    name: 'Durim',
                    country: 'USA'
                },
                {
                    name:'Adam',
                    country:'USA'
                },
                {
                    name:'Angela',
                    country:'USA',
                },
                {
                    name:'Dilrukshi',
                    country:'Sri Lanka',
                },
                {
                    name:'Karolina',
                    country:'USA',
                },
                {
                    name:'Rohit',
                    country:'USA',
                },

            ];

            return contributors;
        }

        function getHighlighted() {
            var img_path = '/static/images/contributors/';

            var contributors = [
                {
                    name:'Michael Bernstein',
                    country:'USA',
                    photo:img_path + 'msb-hoover-200.jpg'
                },
                {
                    name:'Rajan',
                    country:'USA',
                    photo:img_path + 'default.png'
                },
                {
                    name:'Neil',
                    country:'USA',
                    photo:img_path + 'default.png'
                },
                {
                    name:'Durim',
                    country:'USA',
                    photo:img_path + 'default.png'
                },
                {
                    name:'Adam',
                    country:'USA',
                    photo:img_path + 'default.png'
                },
                {
                    name:'Angela',
                    country:'USA',
                    photo:img_path + 'default.png'
                },
                {
                    name:'Dilrukshi',
                    country:'Sri Lanka',
                    photo:img_path + 'default.png'
                },
            ];

            return contributors;
        }
    }
})();
